import datetime
from django.utils.timezone import now
from sms.sayqal import SayqalSms
from celery import shared_task


@shared_task
def send_payment_reminders():
    from data.payment.models import InstallmentPayment
    today = now().date()
    sms_client = SayqalSms()

    for isntallment in InstallmentPayment.objects.all():
        student = isntallment.student
        phone_number = getattr(student.user_account, "phone_number", None)

        if not phone_number:
            continue  # agar studentda telefon raqam yo'q bo'lsa, o'tkazib yuboramiz

        for payment in isntallment.installment_payments:
            due_date = datetime.datetime.strptime(payment["payment_date"], "%Y-%m-%d").date()
            days_left = (due_date - today).days

            if days_left in [5, 3, 1]:
                message = (
                    f"Hurmatli {student.full_name}, "
                    f"{payment['amount']} so'm to'lovingizning muddati {due_date} sanasida tugaydi. "
                    f"Sizda {days_left} kun qoldi."
                )

                sms_client.send_sms(phone_number, message)

