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
    Yangi ma'lumotlar qo'shiladi, mavjudlar yangilanadi.
    """
    try:
        # Excel faylni o'qish (header qatorini o'qimaymiz)
        df = pd.read_excel(file_path, sheet_name='report', header=None)

        # Bo'sh qatorlarni olib tashlash
        df = df.dropna(how='all')

        # Transaksiya ichida barcha operatsiyalarni bajarish
        with transaction.atomic():
            created_count = 0
            updated_count = 0
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
                    faculty, created = Faculty.objects.get_or_create(
                        name=str(row[3]).strip()
                    )

                    # Mutaxassislikni yaratish yoki olish
                    specialization, created = Specialization.objects.get_or_create(
                        code=str(row[4]).strip(),
                        defaults={
                            'name': str(row[5]).strip(),
                            'faculty': faculty
                        }
                    )

                    # Talabani topish yoki yaratish (JSHSHIR bo'yicha)
                    jshshir = str(row[1]).strip()
                    try:
                        # Mavjud talabani topish
                        student = Student.objects.get(jshshir=jshshir)
                        is_new = False

                        # Eski ma'lumotlarni saqlab olish
                        old_data = {
                            'full_name': student.full_name,
                            'status': student.status,
                            'specialization': student.specialization,
                            'course': student.course,
                            'education_type': student.education_type,
                            'education_form': student.education_form,
                            'group': student.group
                        }
                    except Student.DoesNotExist:
                        # Yangi talaba yaratish
                        student = Student(jshshir=jshshir)
                        is_new = True
                        old_data = None

                    # Yangi ma'lumotlarni olish
                    new_data = {
                        'full_name': str(row[0]).strip(),
                        'status': str(row[2]).strip(),
                        'specialization': specialization,
                        'course': str(row[6]).strip(),
                        'education_type': str(row[7]).strip(),
                        'education_form': str(row[8]).strip(),
                        'group': str(row[9]).strip()
                    }

                    # Talaba ma'lumotlarini yangilash
                    student.full_name = new_data['full_name']
                    student.status = new_data['status']
                    student.specialization = new_data['specialization']
                    student.course = new_data['course']
                    student.education_type = new_data['education_type']
                    student.education_form = new_data['education_form']
                    student.group = new_data['group']

                    # Validatsiya
                    student.full_clean()
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

                    # Shartnomani topish yoki yaratish
                    try:
                        contract = Contract.objects.get(student=student)
                        contract_old_data = {
                            'contract_type': contract.contract_type,
                            'initial_balance_dt': contract.initial_balance_dt,
                            'initial_balance_kt': contract.initial_balance_kt,
                            'period_amount_dt': contract.period_amount_dt,
                            'returned_amount_dt': contract.returned_amount_dt,
                            'paid_amount_kt': contract.paid_amount_kt,
                            'final_balance_dt': contract.final_balance_dt,
                            'final_balance_kt': contract.final_balance_kt,
                            'payment_percentage': contract.payment_percentage
                        }
                    except Contract.DoesNotExist:
                        contract = Contract(student=student)
                        contract_old_data = None

                    # Shartnoma ma'lumotlarini yangilash
                    contract.contract_type = str(row[10]).strip()
                    contract.initial_balance_dt = float(row[11])
                    contract.initial_balance_kt = float(row[12])
                    contract.period_amount_dt = float(row[13])
                    contract.returned_amount_dt = float(row[14])
                    contract.paid_amount_kt = float(row[15])
                    contract.final_balance_dt = float(row[16])
                    contract.final_balance_kt = float(row[17])
                    contract.payment_percentage = float(row[18])

                    contract.full_clean()
                    contract.save()

                    if is_new:
                        created_count += 1
                    else:
                        # Faqatgina ma'lumotlari o'zgargan studentlarni hisoblash
                        student_changed = False
                        contract_changed = False

                        # Student ma'lumotlari o'zgarganligini tekshirish
                        if old_data:
                            for key, old_value in old_data.items():
                                if getattr(student, key) != old_value:
                                    student_changed = True
                                    break

                        # Shartnoma ma'lumotlari o'zgarganligini tekshirish
                        if contract_old_data:
                            for key, old_value in contract_old_data.items():
                                if getattr(contract, key) != old_value:
                                    contract_changed = True
                                    break

                        # Agar student yoki shartnoma ma'lumotlari o'zgarganda
                        if student_changed or contract_changed:
                            updated_count += 1

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
                'updated_count': updated_count,
                'message': f"Muvaffaqiyatli import qilindi: {created_count} ta yangi, {updated_count} ta yangilandi"
            }

    except Exception as e:
        return {
            'success': False,
            'message': f"Import jarayonida xato: {str(e)}"
        }


def import_payments_from_excel(file_path):
    """
    To'lovlar excel faylidan ma'lumotlarni import qilish
    Faqat yangi to'lovlar qo'shiladi, mavjud to'lovlar yangilanmaydi.
    """
    try:
        df = pd.read_excel(file_path, sheet_name='Лист1', header=None)
        df = df.dropna(how='all')

        with transaction.atomic():
            created_count = 0
            skipped_count = 0
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
                    student = Student.objects.get(jshshir=str(row[0]).strip())

                    # To'lovni topish (payment_id bo'yicha) - agar mavjud bo'lsa o'tkazib yuborish
                    payment_id = str(row[2]).strip()
                    if Payment.objects.filter(payment_id=payment_id).exists():
                        skipped_count += 1
                        continue  # Mavjud to'lovni o'tkazib yuborish

                    # Yangi to'lov yaratish
                    payment = Payment(
                        student=student,
                        contract_number=str(row[1]).strip(),
                        payment_id=payment_id,
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
                'skipped_count': skipped_count,
                'message': f"Muvaffaqiyatli import qilindi: {created_count} ta yangi to'lov qo'shildi, {skipped_count} ta mavjud to'lov o'tkazib yuborildi"
            }

    except Exception as e:
        return {
            'success': False,
            'message': f"To'lovlar importida xato: {str(e)}"
        }
