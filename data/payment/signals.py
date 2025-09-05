from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from data.contract.services import add_contract_balance
from data.payment.models import Payment, InstallmentPayment, ActionHistory
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

        # history yozish
        ActionHistory.objects.create(
            student=student,
            action_type="PAYMENT_CREATED",
            description=f"{instance.amount} so'm to'lov qo'shildi ({instance.payment_date.date()})",
            changed_by=None  # agar signal bo‘lsa, kim qo‘shganini bilmaymiz
        )

        InstallmentPayment.objects.filter(student=student).update(custom=True)

        #  Avval StudentUser dan olish
        student_user = getattr(student, "user_account", None)
        phone_number = None
        if student_user and student_user.phone_number:
            phone_number = student_user.phone_number

        # Agar StudentUser da bo‘lmasa → Student jadvalidan olish
        elif student.phone_number:
            phone_number = student.phone_number

        print(f"Topilgan phone_number: {phone_number}")

        # Agar umuman topilmasa → SMS yuborilmaydi
        if not phone_number:
            print(f"❌ Telefon raqami topilmadi: {student.full_name} ({student.jshshir})")
            return

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
