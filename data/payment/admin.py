from django.contrib import admin

from data.payment.models import InstallmentPayment, Payment


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "installment_count", "show_splits")

    def show_splits(self, obj):
        return ", ".join([f'{split["amount"]} ({split["payment_date"]})' for split in obj.installment_payments])

    show_splits.short_description = "Splits"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'amount',
        'payment_date',
    )
