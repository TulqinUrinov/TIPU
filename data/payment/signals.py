from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from data.contract.services import add_contract_balance
from data.payment.models import Payment, InstallmentPayment
from data.contract.models import Contract
from sms import SayqalSms


def recalc_for_student(student):
    contract = Contract.objects.filter(student=student).first()
    if contract:
        contract.recalculate_contract()


@receiver(post_save, sender=Payment)
def on_payment_save(sender, instance, created, **kwargs):
    print("Signal ishladi:", created)
    print("Student:", instance.student.full_name)
    student = instance.student
    recalc_for_student(instance.student)

    if created:
        # Student orqali contract olish
        contract = instance.student.contract.first()
        if contract:
            add_contract_balance(contract, instance.amount)

        # agar studentda user_account va phone_number bo‘lsa sms yuborish
        phone_number = getattr(student.user_account, "phone_number", None) if hasattr(student, "user_account") else None
        print(f"phone_number: {phone_number}")

        if phone_number:
            sms_client = SayqalSms()

            message = (f"Hurmatli talaba, sizning "
                       f"{instance.payment_date.strftime('%d-%m-%Y')} "
                       f"sanasida {instance.amount} so'm to'lovingiz qabul qilindi.")

            response = sms_client.send_sms(phone_number, message)
            print("SMS yuborildi:", response.text)


@receiver(post_delete, sender=Payment)
def on_payment_delete(sender, instance, **kwargs):
    recalc_for_student(instance.student)


@receiver(post_save, sender=InstallmentPayment)
def on_installment_save(sender, instance, **kwargs):
    recalc_for_student(instance.student)


@receiver(post_delete, sender=InstallmentPayment)
def on_installment_delete(sender, instance, **kwargs):
    recalc_for_student(instance.student)

# @receiver(post_save, sender=Payment)
# def on_payment_create(sender, instance, created, **kwargs):
#     if created:
#         # Student orqali contract olish
#         contract = instance.student.contract.first()
#         add_contract_balance(contract, instance.amount)  # to'lov + bo'ladi

# @receiver(post_save, sender=InstallmentPayment)
# def on_installment_payment_save(sender, instance, **kwargs):
#     recalc_for_student(instance.payment.student)
#
#
# @receiver(post_delete, sender=InstallmentPayment)
# def on_installment_payment_delete(sender, instance, **kwargs):
#     recalc_for_student(instance.payment.student)
