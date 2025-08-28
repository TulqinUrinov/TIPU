from django.db.models import Sum, DecimalField, ExpressionWrapper, Value, F
from django.db.models.functions import Coalesce, NullIf
from rest_framework import serializers

from data.payment.models import Payment, InstallmentPayment
from data.student.models import Student


class StudentEduYearSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    contract = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    left = serializers.SerializerMethodField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Student
        fields = (
            'id',
            'full_name',
            'jshshir',
            'phone_number',
            'contract',
            'total_paid',
            'left',
            "percentage",
        )

    def get_phone_number(self, obj: Student) -> str:
        if hasattr(obj, "user_account"):
            return obj.user_account.phone_number
        elif obj.phone_number:
            return obj.phone_number
        return None

    def get_contract(self, obj: Student):
        contract = obj.contract.first()
        return contract.period_amount_dt if contract else None

    def get_total_paid(self, obj: Student):
        total_paid = Payment.objects.filter(student=obj).aggregate(total=Sum("amount"))["total"]
        return total_paid or 0

    def get_left(self, obj: Student):
        # kontrakt summasi
        contract = obj.contract.first()
        contract_sum = contract.period_amount_dt if contract else 0

        # qancha to'lov qilingan
        total_paid = Payment.objects.filter(student=obj).aggregate(total=Sum("amount"))["total"] or 0

        # left hisoblash: kontrakt summasi - to'langan summa
        left = contract_sum - total_paid
        return max(left, 0)  # manfiy chiqmasligi uchun


# Retrieve
class StudentSerializer(serializers.ModelSerializer):
    specialization = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    contract = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    left = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id',
            'full_name',
            'jshshir',
            'specialization',
            'phone_number',
            'course',
            'group',
            'contract',
            'total_paid',
            'left',
        )

    def get_phone_number(self, obj: Student) -> str:
        if hasattr(obj, "user_account"):
            return obj.user_account.phone_number
        return None

    def get_specialization(self, obj: Student):
        return obj.specialization.name

    def get_contract(self, obj: Student):
        contract = obj.contract.first()
        return contract.period_amount_dt if contract else None

    def get_total_paid(self, obj: Student):
        total_paid = Payment.objects.filter(student=obj).aggregate(total=Sum("amount"))["total"]
        return total_paid or 0

    def get_left(self, obj: Student):
        # kontrakt summasi
        contract = obj.contract.first()
        contract_sum = contract.period_amount_dt if contract else 0

        # qancha to'lov qilingan
        total_paid = Payment.objects.filter(student=obj).aggregate(total=Sum("amount"))["total"] or 0

        # left hisoblash: kontrakt summasi - to'langan summa
        left = contract_sum - total_paid
        return max(left, 0)  # manfiy chiqmasligi uchun


# Statistics
class StudentStatisticsSerializer(serializers.ModelSerializer):
    total_students = serializers.SerializerMethodField()
    # debt_students = serializers.SerializerMethodField()
    # paid_students = serializers.SerializerMethodField()
    no_hemis_students = serializers.SerializerMethodField()
    hemis_students = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            "total_students",
            "no_hemis_students",
            "hemis_students",
            # "debt_students",
            # "paid_students",
        )

    def get_queryset(self):
        request = self.context.get("request")
        filters = self.context.get("filters", {"is_archived": False})
        edu_year = self.context.get("edu_year")

        queryset = Student.objects.filter(student_years__education_year_id=edu_year, **filters).annotate(
            contract_amount=Coalesce(
                F("contract__period_amount_dt"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            left_sum=Coalesce(
                Sum("contract_payments__left"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
        ).annotate(
            total_paid=F("contract_amount") - F("left_sum"),
            percentage=ExpressionWrapper(
                (F("total_paid") * Value(100, output_field=DecimalField()))
                / NullIf(F("contract_amount"), Value(0, output_field=DecimalField())),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        )

        # percentage bo‘yicha filter
        percentage_range = request.query_params.get("percentage") if request else None
        if percentage_range:
            if "-" in percentage_range:
                start, end = map(float, percentage_range.split("-"))
                queryset = queryset.filter(
                    percentage__gte=start,
                    percentage__lte=end
                )
            else:
                value = float(percentage_range)
                queryset = queryset.filter(percentage=value)

        return queryset

    def get_total_students(self, obj: Student) -> int:
        total_students = self.get_queryset().count()
        return total_students

    def get_no_hemis_students(self, obj: Student):
        # StudentUser accounti mavjud bo'lgan studentlar
        return self.get_queryset().filter(
            is_archived=False,
            user_account__isnull=False
        ).count()

    def get_hemis_students(self, obj: Student):
        # StudentUser accounti yo'q bo'lgan studentlar
        return self.get_queryset().filter(
            is_archived=False,
            user_account__isnull=True
        ).count()

    # def get_debt_students(self, obj):
    #     # Qarzdor: InstallmentPayment.left > 0
    #     debt_students = self.get_queryset().filter(
    #         is_archived=False,
    #         contract_payments__left__gt=0
    #     ).distinct().count()
    #     return debt_students
    #
    # def get_paid_students(self, obj):
    #     # To‘liq to‘lagan: InstallmentPayment.left == 0
    #     paid_students = self.get_queryset().filter(
    #         is_archived=False,
    #         contract_payments__left=0
    #     ).distinct().count()
    #     return paid_students


# Send sms for choosen students
class SendSmsSerializer(serializers.Serializer):
    message = serializers.CharField()
    students = serializers.ListField(
        child=serializers.CharField(),  # JShShIR
        allow_empty=False,
        required=False,
    )
    send_all = serializers.BooleanField(required=False, default=False)
