from django.contrib import admin

from data.payment.models import InstallmentPayment, Payment, ActionHistory


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
        'id',
        'amount',
        'payment_date',
        'source_file',
    )


@admin.register(ActionHistory)
class ActionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'action_type',
        'description',
        'canceled_by',
        'created_at',
    )
