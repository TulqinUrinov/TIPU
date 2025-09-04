import datetime
from django.utils.timezone import now
from sms.sayqal import SayqalSms
from celery import shared_task


@shared_task
def send_payment_reminders():
    from data.payment.models import InstallmentPayment, ReminderConfig
    today = now().date()
    sms_client = SayqalSms()

    # DB dan kunlarni dinamik olish
    days_list = list(
        ReminderConfig.objects.filter(is_active=True).values_list("days_before", flat=True)
    )

    for installment in InstallmentPayment.objects.all():
        student = installment.student

        # telefon raqam olish
        student_user = getattr(student, "user_account", None)
        phone_number = (
            student_user.phone_number if student_user and student_user.phone_number
            else student.phone_number
        )
        if not phone_number:
            continue

        for payment in installment.installment_payments:
            due_date = datetime.datetime.strptime(payment["payment_date"], "%Y-%m-%d").date()
            days_left = (due_date - today).days

            if days_left in days_list:
                message = (
                    f"Hurmatli {student.full_name}, "
                    f"{payment['amount']} so'm kontrakt to'lovingizning muddati {due_date} sanasida tugaydi. "
                    f"Kontrakt to'loviga {days_left} kun qoldi. "
                    f"Vaqtida to'lashni so'raymiz!"
                )
                sms_client.send_sms(phone_number, message)

# @shared_task
# def send_payment_reminders():
#     from data.payment.models import InstallmentPayment
#     today = now().date()
#     sms_client = SayqalSms()
#
#     for isntallment in InstallmentPayment.objects.all():
#         student = isntallment.student
#
#         student_user = getattr(student, "user_account", None)
#         phone_number = None
#         if student_user and student_user.phone_number:
#             phone_number = student_user.phone_number
#
#         elif student.phone_number:
#             phone_number = student.phone_number
#
#         if not phone_number:
#             continue
#
#         for payment in isntallment.installment_payments:
#             due_date = datetime.datetime.strptime(payment["payment_date"], "%Y-%m-%d").date()
#             days_left = (due_date - today).days
#
#             if days_left in [5, 3, 1]:
#                 message = (
#                     f"Hurmatli {student.full_name}, "
#                     f"{payment['amount']} so'm kontrakt to'lovingizning muddati {due_date} sanasida tugaydi. "
#                     f"Kontrakt to'lovi kuniga {days_left} kun qoldi."
#                     f"Toshkent Iqtisodiyot va Pedagogika Universitet bilan tuzilgan shartnomaga "
#                     f"asosan kontrakt to'lovini vaqtida to'lashingizni so'raymiz!"
#                     f"Murojaat uchun: "
#                 )
#
#                 sms_client.send_sms(phone_number, message)
