from rest_framework import serializers

from data.student.models import Student

# O'quv yiliga tegishli barcha talabalar ro'yxati uchun
class StudentEduYearSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    contract = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id',
            'full_name',
            'jshshir',
            'phone_number',
            'contract',
            # qancha to'langanligi qo'shiladi
        )

    def get_phone_number(self, obj: Student) -> str:
        if hasattr(obj, "user_account"):
            return obj.user_account.phone_number
        return None

    def get_contract(self, obj: Student):
        contract = obj.contract.first()
        return contract.period_amount_dt if contract else None
