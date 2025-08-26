from django.contrib import admin

from data.contract.models import ContractBalance


class ContractAdmin(admin.ModelAdmin):
    list_display = (
        ''
    )

@admin.register(ContractBalance)
class ContractBalanceAdmin(admin.ModelAdmin):
    list_display = ('contract', "change", "final_balance")



