import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
import traceback

from data.contract.models import Contract
from data.faculty.models import Faculty
from data.payment.models import Payment
from data.specialization.models import Specialization
from data.student.models import Student


def import_students_from_excel(file_path):
    """
    Excel fayldan ma'lumotlarni import qilish.
    Bitta xatolik bo'lsa ham hech narsa saqlanmaydi.
    """
    try:
        # Excel faylni o'qish (header qatorini o'qimaymiz)
        df = pd.read_excel(file_path, sheet_name='report', header=None)

        # Bo'sh qatorlarni olib tashlash
        df = df.dropna(how='all')

        # Transaksiya ichida barcha operatsiyalarni bajarish
        with transaction.atomic():
            created_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # Header qatorlarini o'tkazib yuborish (0 va 1-qatorlar)
                    if index in [0, 1]:
                        continue

                    # Ma'lumotlarni tekshirish (bo'sh yoki NaN bo'lmasligi kerak)
                    required_fields = [
                        (0, "Talaba F.I.Sh"),
                        (1, "JSHSHIR"),
                        (2, "Talaba statusi"),
                        (3, "Fakultet nomi"),
                        (4, "Mutaxassislik kodi"),
                        (5, "Mutaxassislik nomi"),
                        (6, "Talaba kursi"),
                        (7, "Taʼlim turi"),
                        (8, "Taʼlim shakli"),
                        (9, "Gruhi"),
                        (10, "Shartnoma shakli")
                    ]

                    for col_index, field_name in required_fields:
                        if pd.isna(row[col_index]) or str(row[col_index]).strip() == "":
                            raise ValidationError(f"{field_name} maydoni bo'sh bo'lishi mumkin emas")

                    # Fakultetni yaratish yoki olish
                    # D(3) - Fakultet nomi
                    faculty, created = Faculty.objects.get_or_create(
                        name=str(row[3]).strip()
                    )

                    # Mutaxassislikni yaratish yoki olish
                    # E(4) - Mutaxassislik kodi, F(5) - Mutaxassislik nomi
                    specialization, created = Specialization.objects.get_or_create(
                        code=str(row[4]).strip(),
                        defaults={
                            'name': str(row[5]).strip(),
                            'faculty': faculty
                        }
                    )

                    # Talabani yaratish
                    # A(0) - Talaba F.I.Sh, B(1) - JSHSHIR, C(2) - Talaba statusi
                    # G(6) - Talaba kursi, H(7) - Taʼlim turi, I(8) - Taʼlim shakli
                    # J(9) - Gruhi
                    student = Student(
                        full_name=str(row[0]).strip(),
                        jshshir=str(row[1]).strip(),
                        status=str(row[2]).strip(),
                        specialization=specialization,
                        course=str(row[6]).strip(),
                        education_type=str(row[7]).strip(),
                        education_form=str(row[8]).strip(),
                        group=str(row[9]).strip()
                    )

                    # Validatsiya
                    student.full_clean()

                    # Saqlash
                    student.save()

                    # Raqamli maydonlarni tekshirish
                    numeric_fields = [
                        (11, "Davr boshiga qoldiq DT"),
                        (12, "Davr boshiga qoldiq KT"),
                        (13, "Shartnoma summasi (DT)"),
                        (14, "Qaytarilgan summa (DT)"),
                        (15, "To'langan summa (KT)"),
                        (16, "Davr ohiriga qoldiq DT"),
                        (17, "Davr ohiriga qoldiq KT"),
                        (18, "To'langan summa foizda")
                    ]

                    for col_index, field_name in numeric_fields:
                        if pd.isna(row[col_index]):
                            raise ValidationError(f"{field_name} maydoni bo'sh bo'lishi mumkin emas")
                        try:
                            float(row[col_index])
                        except (ValueError, TypeError):
                            raise ValidationError(f"{field_name} raqam bo'lishi kerak")

                    # Shartnoma yaratish
                    # K(10) - Shartnoma shakli
                    # L(11) - Davr boshiga qoldiq DT, M(12) - Davr boshiga qoldiq KT
                    # N(13) - Shartnoma summasi (DT), O(14) - Qaytarilgan summa (DT)
                    # P(15) - To'langan summa (KT), Q(16) - Davr ohiriga qoldiq DT
                    # R(17) - Davr ohiriga qoldiq KT, S(18) - To'langan summa foizda
                    contract = Contract(
                        student=student,
                        contract_type=str(row[10]).strip(),
                        initial_balance_dt=float(row[11]),
                        initial_balance_kt=float(row[12]),
                        period_amount_dt=float(row[13]),
                        returned_amount_dt=float(row[14]),
                        paid_amount_kt=float(row[15]),
                        final_balance_dt=float(row[16]),
                        final_balance_kt=float(row[17]),
                        payment_percentage=float(row[18])
                    )

                    contract.full_clean()
                    contract.save()

                    created_count += 1

                except Exception as e:
                    # Xatolikni qayd etish
                    error_msg = f"Qator {index + 1}: {str(e)}"
                    errors.append(error_msg)
                    # Xatolikni log qilish
                    print(f"Xato: {error_msg}")
                    print(traceback.format_exc())

            # Agar xatoliklar bo'lsa, exception ko'tarish
            if errors:
                error_message = "\n".join(errors)
                raise ValidationError(f"Importda xatoliklar topildi:\n{error_message}")

            return {
                'success': True,
                'created_count': created_count,
                'message': f"Muvaffaqiyatli import qilindi: {created_count} ta talaba"
            }

    except Exception as e:
        return {
            'success': False,
            'message': f"Import jarayonida xato: {str(e)}"
        }


def import_payments_from_excel(file_path):
    """
    To'lovlar excel faylidan ma'lumotlarni import qilish
    """
    try:
        df = pd.read_excel(file_path, sheet_name='Лист1', header=None)
        df = df.dropna(how='all')

        with transaction.atomic():
            created_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # Header qatorini o'tkazib yuborish (0-qator)
                    if index == 0:
                        continue

                    # Majburiy maydonlarni tekshirish
                    required_fields = [
                        (0, "JShShIR"),
                        (1, "Shartnoma raqami"),
                        (2, "To'lov ID"),
                        (3, "To'lov summasi"),
                        (4, "To'lov sanasi"),
                        (5, "To'lov maqsadi")
                    ]

                    for col_index, field_name in required_fields:
                        if pd.isna(row[col_index]) or str(row[col_index]).strip() == "":
                            raise ValidationError(f"{field_name} maydoni bo'sh bo'lishi mumkin emas")

                    # Raqamli maydonlarni tekshirish
                    if pd.isna(row[3]):
                        raise ValidationError("To'lov summasi bo'sh bo'lishi mumkin emas")
                    try:
                        float(row[3])
                    except (ValueError, TypeError):
                        raise ValidationError("To'lov summasi raqam bo'lishi kerak")

                    # Sana formatini tekshirish
                    try:
                        payment_date = datetime.strptime(str(row[4]), '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        raise ValidationError("To'lov sanasi noto'g'ri formatda. Format: YYYY-MM-DD HH:MM:SS")

                    # Talabani topish
                    # A(0) - JShShIR
                    student = Student.objects.get(jshshir=str(row[0]).strip())

                    # To'lovni yaratish
                    # B(1) - Shartnoma raqami, C(2) - To'lov ID
                    # D(3) - To'lov summasi, E(4) - To'lov sanasi
                    # F(5) - To'lov maqsadi
                    payment = Payment(
                        student=student,
                        contract_number=str(row[1]).strip(),
                        payment_id=str(row[2]).strip(),
                        amount=float(row[3]),
                        payment_date=payment_date,
                        purpose=str(row[5]).strip()
                    )

                    payment.full_clean()
                    payment.save()
                    created_count += 1

                except Student.DoesNotExist:
                    error_msg = f"Qator {index + 1}: JSHSHIR {row[0]} bo'yicha talaba topilmadi"
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Qator {index + 1}: {str(e)}"
                    errors.append(error_msg)
                    print(f"Xato: {error_msg}")
                    print(traceback.format_exc())

            if errors:
                error_message = "\n".join(errors)
                raise ValidationError(f"To'lovlar importida xatoliklar:\n{error_message}")

            return {
                'success': True,
                'created_count': created_count,
                'message': f"Muvaffaqiyatli import qilindi: {created_count} ta to'lov"
            }

    except Exception as e:
        return {
            'success': False,
            'message': f"To'lovlar importida xato: {str(e)}"
        }
