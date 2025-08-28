from rest_framework import serializers
from .models import InstallmentPayment, Payment


# Bo'lib to'lash
class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = (
            "id",
            "student",
            "installment_count",
            "left",
            "installment_payments",
            "custom",
        )

    def validate(self, data):
        """Check that installment_count matches number of splits"""
        splits = data.get("installment_payments", [])
        count = data.get("installment_count")
        if count != len(splits):
            raise serializers.ValidationError("installment_count va splits soni mos emas!")
        return data


# Barchasini yangilash
class InstallmentBulkUpdateSerializer(serializers.Serializer):
    installment_count = serializers.IntegerField()
    payment_dates = serializers.ListField(
        child=serializers.DateField(),
        allow_empty=False
    )

    def validate(self, attrs):
        count = attrs['installment_count']
        dates = attrs['payment_dates']

        if count != len(dates):
            raise serializers.ValidationError(
                "installment_count va payment_dates soni mos emas!"
            )
        return attrs


# To'lovlar tarixi
class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id',
            'payment_id',
            'amount',
            'payment_date',
        )
