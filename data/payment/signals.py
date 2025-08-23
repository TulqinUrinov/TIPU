from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from data.contract.services import add_contract_balance
from data.payment.models import Payment, InstallmentPayment
from data.contract.models import Contract


def recalc_for_student(student):
    contract = Contract.objects.filter(student=student).first()
    if contract:
        contract.recalculate_contract()


@receiver(post_save, sender=Payment)
def on_payment_save(sender, instance, **kwargs):
    recalc_for_student(instance.student)


@receiver(post_delete, sender=Payment)
def on_payment_delete(sender, instance, **kwargs):
    recalc_for_student(instance.student)


@receiver(post_save, sender=InstallmentPayment)
def on_installment_save(sender, instance, **kwargs):
    recalc_for_student(instance.student)


@receiver(post_delete, sender=InstallmentPayment)
def on_installment_delete(sender, instance, **kwargs):
    recalc_for_student(instance.student)


@receiver(post_save, sender=Payment)
def on_payment_create(sender, instance, created, **kwargs):
    if created:
        # Student orqali contract olish
        contract = instance.student.contract.first()
        add_contract_balance(contract, instance.amount)  # to'lov + bo'ladi

# @receiver(post_save, sender=InstallmentPayment)
# def on_installment_payment_save(sender, instance, **kwargs):
#     recalc_for_student(instance.payment.student)
#
#
# @receiver(post_delete, sender=InstallmentPayment)
# def on_installment_payment_delete(sender, instance, **kwargs):
#     recalc_for_student(instance.payment.student)
