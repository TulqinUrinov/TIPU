from django.db.models.signals import post_save
from django.dispatch import receiver
from data.file.models import Files, ContractFiles


@receiver(post_save, sender=Files)
def delete_old_contracts_when_template_updated(sender, instance, created, **kwargs):
    file_type = instance.file_type

    if file_type == "MUQOBIL":

        contracts = ContractFiles.objects.filter(student__user_account__isnull=False)
    elif file_type == "HEMIS":
        contracts = ContractFiles.objects.filter(student__user_account__isnull=True)
    else:
        return
    contracts.delete()
