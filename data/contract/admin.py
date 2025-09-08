from django.contrib import admin

from data.contract.models import ContractBalance


@admin.register(ContractBalance)
class ContractBalanceAdmin(admin.ModelAdmin):
    list_display = ('contract', "change", "final_balance")
