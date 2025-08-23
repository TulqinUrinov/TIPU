from django.db.models import Sum
from rest_framework import serializers

from data.payment.models import Payment
from data.student.models import Student


# O'quv yiliga tegishli barcha talabalar ro'yxati uchun
class StudentEduYearSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    contract = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id',
            'full_name',
            'jshshir',
            'phone_number',
            'contract',
            'total_paid',
        )

    def get_phone_number(self, obj: Student) -> str:
        if hasattr(obj, "user_account"):
            return obj.user_account.phone_number
        return None

    def get_contract(self, obj: Student):
        contract = obj.contract.first()
        return contract.period_amount_dt if contract else None

    def get_total_paid(self, obj: Student):
        total_paid = Payment.objects.filter(student=obj).aggregate(total=Sum("amount"))["total"]
        return total_paid or 0
