from rest_framework import serializers
from .models import InstallmentPayment

class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = ("id", "student", "installment_count","left", "installment_payments")

    def validate(self, data):
        """Check that installment_count matches number of splits"""
        splits = data.get("installment_payments", [])
        count = data.get("installment_count")
        if count != len(splits):
            raise serializers.ValidationError("installment_count va splits soni mos emas!")
        return data
