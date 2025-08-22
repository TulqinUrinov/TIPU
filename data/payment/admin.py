from django.contrib import admin

from data.payment.models import InstallmentPayment


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "count",
        "amount",
        "payment_date",
        "left",
    )
