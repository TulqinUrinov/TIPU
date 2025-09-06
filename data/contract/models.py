from django.db import models
from typing import TYPE_CHECKING

from data.common.models import BaseModel
from data.payment.models import InstallmentPayment

if TYPE_CHECKING:
    from data.student.models import Student
    from data.file.models import Files


class Contract(BaseModel):
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        related_name="contract"
    )

    source_file: "Files" = models.ForeignKey(
        "file.Files",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts"
    )

    contract_type = models.CharField(
        max_length=100,
        verbose_name="Shartnoma shakli"
    )  # uch tomonlama, ikki tomonlama

    initial_balance_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr boshiga qoldiq (DT)",
        default=0
    )

    initial_balance_kt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr boshiga qoldiq (KT)",
        default=0
    )

    period_amount_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Shartnoma Summasi (DT)",
        default=0
    )

    returned_amount_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Qaytarilgan summa (DT)",
        default=0
    )

    paid_amount_kt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="To'langan summa (KT)",
        default=0
    )

    final_balance_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr ohiriga qoldiq (DT)",
        default=0
    )

    final_balance_kt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr ohiriga qoldiq (KT)",
        default=0
    )

    payment_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="To'langan summa foizda",
        default=0
    )

    def __str__(self):
        return f"{self.student.full_name} - {self.contract_type}"

    def recalculate_contract(self):
        student = self.student

        # 1. Umumiy kontrakt summasini hisoblash (boshlang'ich balansni hisobga olib)
        umumiy_summasi = (
                self.period_amount_dt
                + self.initial_balance_dt
                - self.initial_balance_kt
        )

        # 2. Barcha installmentsni reset qilish
        installments = student.contract_payments.all()

        for inst in installments:
            updated_splits = []
            for split in inst.installment_payments:
                split["left"] = Decimal(split["amount"])  # boshlang'ichda amount = left
                updated_splits.append(split)

            # Decimal bo'lgan dictlarni floatga aylantirish
            inst.installment_payments = decimal_to_float(updated_splits)
            inst.left = float(sum(Decimal(s["left"]) for s in updated_splits))

            # signalni chaqirmasdan update
            InstallmentPayment.objects.filter(id=inst.id).update(
                installment_payments=inst.installment_payments,
                left=inst.left
            )

        # inst.save()
        # inst.save(update_fields=["installment_payments", "left"])

        # 3. Barcha paymentsni qo'llash
        payments = student.payments.order_by("payment_date")
        for payment in payments:
            amount = Decimal(payment.amount)
            for inst in installments:
                splits = inst.installment_payments
                updated_splits = []
                for split in splits:
                    if amount <= 0:
                        updated_splits.append(split)
                        continue

                    left_val = Decimal(split.get("left", split["amount"]))
                    if left_val <= 0:
                        updated_splits.append(split)
                        continue

                    if amount >= left_val:
                        amount -= left_val
                        split["left"] = 0
                    else:
                        split["left"] = left_val - amount
                        amount = 0
                    updated_splits.append(split)

                # Decimal bo'lgan dictlarni floatga aylantirish
                inst.installment_payments = decimal_to_float(updated_splits)
                inst.left = float(sum(Decimal(s["left"]) for s in updated_splits))

                # signalni chaqirmasdan update
                InstallmentPayment.objects.filter(id=inst.id).update(
                    installment_payments=inst.installment_payments,
                    left=inst.left)

                # # inst.save()
                # # inst.save(update_fields=["installment_payments", "left"])

        # 4. Contractni yangilash
        total_paid = sum(Decimal(p.amount) for p in payments)
        self.paid_amount_kt = total_paid
        self.final_balance_dt = umumiy_summasi - total_paid
        self.payment_percentage = (
            (total_paid / umumiy_summasi) * 100 if umumiy_summasi > 0 else 0
        )
        self.save()


class ContractBalance(BaseModel):
    contract = models.ForeignKey(
        "contract.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="balances"
    )
    change = models.DecimalField(max_digits=15, decimal_places=2,
                                 default=0)  # o'zgarish (to'lov qo'shilsa +, qaytarilsa -)
    final_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # yakuniy balans


from decimal import Decimal


def decimal_to_float(obj):
    """Recursive converter: Decimal → float"""
    if isinstance(obj, list):
        return [decimal_to_float(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)  # yoki str(obj) agar matn ko‘rinishda saqlashni xohlasang
    return obj
