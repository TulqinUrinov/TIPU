import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
import traceback

from django.utils import timezone

from data.contract.models import Contract
from data.education_year.models import EducationYear
from data.faculty.models import Faculty
from data.payment.models import Payment, InstallmentPayment
from data.specialization.models import Specialization
from data.student.models import Student
from data.studentedu_year.models import StudentEduYear

from decimal import Decimal, ROUND_HALF_UP


def to_decimal(value, places=2):
    """
    Sonni decimalga aylantirib, kerakli joygacha yaxlitlaydi.
    Masalan: 123.4567 -> 123.46
    """
    return Decimal(str(value)).quantize(Decimal(f'1.{"0" * places}'), rounding=ROUND_HALF_UP)


def import_students_from_excel(file_path, education_year):
    """
    Excel fayldan ma'lumotlarni import qiladi.
    Bulk create orqali saqlaydi.
    """
    try:
        edu_year = EducationYear.objects.get(id=education_year)
        df = pd.read_excel(file_path, sheet_name='report', header=None)
        df = df.dropna(how='all')

        with transaction.atomic():
            students_to_create = []
            contracts_to_create = []
            student_edu_years_to_create = []
            installments_to_create = []

            created_count = 0
            updated_count = 0
            errors = []

            # 1. Student obyektlarini tayyorlash
            for index, row in df.iterrows():
                try:
                    if index in [0, 1]:
                        continue

                    # Majburiy maydonlar
                    required_fields = [
                        (0, "Talaba F.I.Sh"), (1, "JSHSHIR"), (2, "Talaba statusi"),
                        (3, "Fakultet nomi"), (4, "Mutaxassislik kodi"), (5, "Mutaxassislik nomi"),
                        (6, "Talaba kursi"), (7, "Taʼlim turi"), (8, "Taʼlim shakli"),
                        (9, "Gruhi"), (10, "Shartnoma shakli")
                    ]
                    for col_index, field_name in required_fields:
                        if pd.isna(row[col_index]) or str(row[col_index]).strip() == "":
                            raise ValidationError(f"{field_name} maydoni bo'sh bo'lishi mumkin emas")

                    # Fakultet va mutaxassislik
                    faculty, _ = Faculty.objects.get_or_create(name=str(row[3]).strip())
                    specialization, _ = Specialization.objects.get_or_create(
                        code=str(row[4]).strip(),
                        defaults={'name': str(row[5]).strip(), 'faculty': faculty}
                    )

                    jshshir = str(row[1]).strip()
                    try:
                        student = Student.objects.get(jshshir=jshshir)
                        is_new = False
                        updated_count += 1
                        # Yangilash
                        student.full_name = str(row[0]).strip()
                        student.status = str(row[2]).strip()
                        student.specialization = specialization
                        student.course = str(row[6]).strip()
                        student.education_type = str(row[7]).strip()
                        student.education_form = str(row[8]).strip()
                        student.group = str(row[9]).strip()
                        student.full_clean()
                        student.save()
                    except Student.DoesNotExist:
                        student = Student(
                            jshshir=jshshir,
                            full_name=str(row[0]).strip(),
                            status=str(row[2]).strip(),
                            specialization=specialization,
                            course=str(row[6]).strip(),
                            education_type=str(row[7]).strip(),
                            education_form=str(row[8]).strip(),
                            group=str(row[9]).strip()
                        )
                        student.full_clean()
                        students_to_create.append(student)
                        is_new = True
                        created_count += 1

                except Exception as e:
                    error_msg = f"Qator {index + 1}: {str(e)}"
                    errors.append(error_msg)
                    print(f"Xato: {error_msg}")
                    print(traceback.format_exc())

            # 2. Yangi studentlarni bazaga saqlash
            if students_to_create:
                Student.objects.bulk_create(students_to_create)

            # 3. Contract, StudentEduYear va InstallmentPayment obyektlarini tayyorlash
            for index, row in df.iterrows():
                if index in [0, 1]:
                    continue

                try:
                    jshshir = str(row[1]).strip()
                    student = Student.objects.get(jshshir=jshshir)

                    # Contract
                    contract = Contract(
                        student=student,
                        contract_type=str(row[10]).strip(),
                        initial_balance_dt=to_decimal(row[11]),
                        initial_balance_kt=to_decimal(row[12]),
                        period_amount_dt=to_decimal(row[13]),
                        returned_amount_dt=to_decimal(row[14]),
                        paid_amount_kt=to_decimal(row[15]),
                        final_balance_dt=to_decimal(row[16]),
                        final_balance_kt=to_decimal(row[17]),
                        payment_percentage=to_decimal(row[18], places=2)
                    )
                    contract.full_clean()
                    contracts_to_create.append(contract)

                    # StudentEduYear
                    student_edu_years_to_create.append(StudentEduYear(student=student, education_year=edu_year))

                    # InstallmentPayment (faqat yangi studentlar)
                    if created_count > 0:
                        amount_per_split = to_decimal(row[13]) / 4
                        start_year = int(str(edu_year).split('-')[0])
                        payment_dates = [
                            datetime(start_year, 10, 10),
                            datetime(start_year, 12, 10),
                            datetime(start_year + 1, 3, 10),
                            datetime(start_year + 1, 5, 10),
                        ]
                        installments_to_create.append(
                            InstallmentPayment(
                                student=student,
                                installment_count=4,
                                installment_payments=[
                                    {"amount": str(amount_per_split), "payment_date": d.strftime("%Y-%m-%d")} for d in
                                    payment_dates]
                            )
                        )

                except Exception as e:
                    error_msg = f"Qator {index + 1}: {str(e)}"
                    errors.append(error_msg)
                    print(f"Xato: {error_msg}")
                    print(traceback.format_exc())

            # 4. Bulk create bajarish
            if contracts_to_create:
                Contract.objects.bulk_create(contracts_to_create)
            if student_edu_years_to_create:
                StudentEduYear.objects.bulk_create(student_edu_years_to_create)
            if installments_to_create:
                InstallmentPayment.objects.bulk_create(installments_to_create)

            # 5. Xatoliklar bo‘lsa
            if errors:
                raise ValidationError(f"Importda xatoliklar topildi:\n" + "\n".join(errors))

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


# def import_students_from_excel(file_path, education_year):
#     """
#     Excel fayldan ma'lumotlarni import qilish.
#     Bitta xatolik bo'lsa ham hech narsa saqlanmaydi.
#     Yangi ma'lumotlar qo'shiladi, mavjudlar yangilanadi.
#     """
#     try:
#         # O'quv yilini olish
#         edu_year = EducationYear.objects.get(id=education_year)
#
#         # Excel faylni o'qish (header qatorini o'qimaymiz)
#         df = pd.read_excel(file_path, sheet_name='report', header=None)
#
#         # Bo'sh qatorlarni olib tashlash
#         df = df.dropna(how='all')
#
#         # Transaksiya ichida barcha operatsiyalarni bajarish
#         with transaction.atomic():
#             created_count = 0
#             updated_count = 0
#             errors = []
#
#             for index, row in df.iterrows():
#                 try:
#                     # Header qatorlarini o'tkazib yuborish (0 va 1-qatorlar)
#                     if index in [0, 1]:
#                         continue
#
#                     # Ma'lumotlarni tekshirish (bo'sh yoki NaN bo'lmasligi kerak)
#                     required_fields = [
#                         (0, "Talaba F.I.Sh"),
#                         (1, "JSHSHIR"),
#                         (2, "Talaba statusi"),
#                         (3, "Fakultet nomi"),
#                         (4, "Mutaxassislik kodi"),
#                         (5, "Mutaxassislik nomi"),
#                         (6, "Talaba kursi"),
#                         (7, "Taʼlim turi"),
#                         (8, "Taʼlim shakli"),
#                         (9, "Gruhi"),
#                         (10, "Shartnoma shakli")
#                     ]
#
#                     for col_index, field_name in required_fields:
#                         if pd.isna(row[col_index]) or str(row[col_index]).strip() == "":
#                             raise ValidationError(f"{field_name} maydoni bo'sh bo'lishi mumkin emas")
#
#                     # Fakultetni yaratish yoki olish
#                     faculty, created = Faculty.objects.get_or_create(
#                         name=str(row[3]).strip()
#                     )
#
#                     # Mutaxassislikni yaratish yoki olish
#                     specialization, created = Specialization.objects.get_or_create(
#                         code=str(row[4]).strip(),
#                         defaults={
#                             'name': str(row[5]).strip(),
#                             'faculty': faculty
#                         }
#                     )
#
#                     # Talabani topish yoki yaratish (JSHSHIR bo'yicha)
#                     jshshir = str(row[1]).strip()
#                     try:
#                         # Mavjud talabani topish
#                         student = Student.objects.get(jshshir=jshshir)
#                         is_new = False
#
#                         # Eski ma'lumotlarni saqlab olish
#                         old_data = {
#                             'full_name': student.full_name,
#                             'status': student.status,
#                             'specialization': student.specialization,
#                             'course': student.course,
#                             'education_type': student.education_type,
#                             'education_form': student.education_form,
#                             'group': student.group
#                         }
#                     except Student.DoesNotExist:
#                         # Yangi talaba yaratish
#                         student = Student(jshshir=jshshir)
#                         is_new = True
#                         old_data = None
#
#                     # Yangi ma'lumotlarni olish
#                     new_data = {
#                         'full_name': str(row[0]).strip(),
#                         'status': str(row[2]).strip(),
#                         'specialization': specialization,
#                         'course': str(row[6]).strip(),
#                         'education_type': str(row[7]).strip(),
#                         'education_form': str(row[8]).strip(),
#                         'group': str(row[9]).strip()
#                     }
#
#                     # Talaba ma'lumotlarini yangilash
#                     student.full_name = new_data['full_name']
#                     student.status = new_data['status']
#                     student.specialization = new_data['specialization']
#                     student.course = new_data['course']
#                     student.education_type = new_data['education_type']
#                     student.education_form = new_data['education_form']
#                     student.group = new_data['group']
#
#                     # Validatsiya
#                     student.full_clean()
#                     student.save()
#
#                     # O‘quv yili bilan bog‘lash
#                     StudentEduYear.objects.get_or_create(
#                         student=student,
#                         education_year=edu_year
#                     )
#
#                     # Raqamli maydonlarni tekshirish
#                     numeric_fields = [
#                         (11, "Davr boshiga qoldiq DT"),
#                         (12, "Davr boshiga qoldiq KT"),
#                         (13, "Shartnoma summasi (DT)"),
#                         (14, "Qaytarilgan summa (DT)"),
#                         (15, "To'langan summa (KT)"),
#                         (16, "Davr ohiriga qoldiq DT"),
#                         (17, "Davr ohiriga qoldiq KT"),
#                         (18, "To'langan summa foizda")
#                     ]
#
#                     for col_index, field_name in numeric_fields:
#                         if pd.isna(row[col_index]):
#                             raise ValidationError(f"{field_name} maydoni bo'sh bo'lishi mumkin emas")
#                         try:
#                             float(row[col_index])
#                         except (ValueError, TypeError):
#                             raise ValidationError(f"{field_name} raqam bo'lishi kerak")
#
#                     # Shartnomani topish yoki yaratish
#                     try:
#                         contract = Contract.objects.get(student=student)
#                         contract_old_data = {
#                             'contract_type': contract.contract_type,
#                             'initial_balance_dt': contract.initial_balance_dt,
#                             'initial_balance_kt': contract.initial_balance_kt,
#                             'period_amount_dt': contract.period_amount_dt,
#                             'returned_amount_dt': contract.returned_amount_dt,
#                             'paid_amount_kt': contract.paid_amount_kt,
#                             'final_balance_dt': contract.final_balance_dt,
#                             'final_balance_kt': contract.final_balance_kt,
#                             'payment_percentage': contract.payment_percentage
#                         }
#                     except Contract.DoesNotExist:
#                         contract = Contract(student=student)
#                         contract_old_data = None
#
#                     # Shartnoma ma'lumotlarini yangilash
#                     contract.contract_type = str(row[10]).strip()
#                     contract.initial_balance_dt = to_decimal(row[11])
#                     contract.initial_balance_kt = to_decimal(row[12])
#                     contract.period_amount_dt = to_decimal(row[13])
#                     contract.returned_amount_dt = to_decimal(row[14])
#                     contract.paid_amount_kt = to_decimal(row[15])
#                     contract.final_balance_dt = to_decimal(row[16])
#                     contract.final_balance_kt = to_decimal(row[17])
#                     contract.payment_percentage = to_decimal(row[18], places=2)
#
#                     # contract.contract_type = str(row[10]).strip()
#                     # contract.initial_balance_dt = float(row[11])
#                     # contract.initial_balance_kt = float(row[12])
#                     # contract.period_amount_dt = float(row[13])
#                     # contract.returned_amount_dt = float(row[14])
#                     # contract.paid_amount_kt = float(row[15])
#                     # contract.final_balance_dt = float(row[16])
#                     # contract.final_balance_kt = float(row[17])
#                     # contract.payment_percentage = float(row[18])
#
#                     contract.full_clean()
#                     contract.save()
#
#                     if is_new:
#                         created_count += 1
#
#                         # Eski paymentlarni o'chirish
#                         InstallmentPayment.objects.filter(student=student).delete()
#
#                         contract = student.contract.first()
#                         if not contract:
#                             raise ValueError("Student uchun contract topilmadi.")
#
#                         amount_per_split = contract.period_amount_dt / 4
#                         start_year = int(str(edu_year).split('-')[0])
#
#                         # Default avtomatik sanalar
#                         payment_dates = [
#                             datetime(start_year, 10, 10),
#                             datetime(start_year, 12, 10),
#                             datetime(start_year + 1, 3, 10),
#                             datetime(start_year + 1, 5, 10),
#                         ]
#
#                         # Splits tayyorlash
#                         installment_payments = []
#                         for payment_date in payment_dates:
#                             installment_payments.append({
#                                 "amount": str(amount_per_split),
#                                 "payment_date": payment_date.strftime("%Y-%m-%d")
#                             })
#
#                         # Installment yaratish
#                         InstallmentPayment.objects.create(
#                             student=student,
#                             installment_count=4,  # faqat 4 bo‘ladi
#                             installment_payments=installment_payments
#                         )
#
#                     else:
#                         # Faqatgina ma'lumotlari o'zgargan studentlarni hisoblash
#                         student_changed = False
#                         contract_changed = False
#
#                         # Student ma'lumotlari o'zgarganligini tekshirish
#                         if old_data:
#                             for key, old_value in old_data.items():
#                                 if getattr(student, key) != old_value:
#                                     student_changed = True
#                                     break
#
#                         # Shartnoma ma'lumotlari o'zgarganligini tekshirish
#                         if contract_old_data:
#                             for key, old_value in contract_old_data.items():
#                                 if getattr(contract, key) != old_value:
#                                     contract_changed = True
#                                     break
#
#                         # Agar student yoki shartnoma ma'lumotlari o'zgarganda
#                         if student_changed or contract_changed:
#                             updated_count += 1
#
#                 except Exception as e:
#                     # Xatolikni qayd etish
#                     error_msg = f"Qator {index + 1}: {str(e)}"
#                     errors.append(error_msg)
#                     # Xatolikni log qilish
#                     print(f"Xato: {error_msg}")
#                     print(traceback.format_exc())
#
#             # Agar xatoliklar bo'lsa, exception ko'tarish
#             if errors:
#                 error_message = "\n".join(errors)
#                 raise ValidationError(f"Importda xatoliklar topildi:\n{error_message}")
#
#             return {
#                 'success': True,
#                 'created_count': created_count,
#                 'updated_count': updated_count,
#                 'message': f"Muvaffaqiyatli import qilindi: {created_count} ta yangi, {updated_count} ta yangilandi"
#             }
#
#     except Exception as e:
#         return {
#             'success': False,
#             'message': f"Import jarayonida xato: {str(e)}"
#         }


def import_payments_from_excel(file_path):
    """
    To'lovlar excel faylidan ma'lumotlarni import qilish.
    Faqat yangi to'lovlar qo'shiladi, mavjud to'lovlar yangilanmaydi.
    Agar bitta qator xato bo'lsa ham – hammasi rollback qilinadi.
    """

    df = pd.read_excel(file_path, sheet_name='Лист1', header=None)
    df = df.dropna(how='all')

    with transaction.atomic():  # rollback uchun
        created_count = 0
        skipped_count = 0

        for index, row in df.iterrows():
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
                    raise ValidationError(f"Qator {index + 1}: {field_name} bo'sh bo'lishi mumkin emas")

            # To'lov summasi
            try:
                # amount = Decimal(str(row[3])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                amount = to_decimal(row[3])

            except (ValueError, TypeError):
                raise ValidationError(f"Qator {index + 1}: To'lov summasi noto'g'ri formatda")

            # # Sana
            # try:
            #     payment_date = datetime.strptime(str(row[4]), '%Y-%m-%d %H:%M:%S')
            # except ValueError:
            #     raise ValidationError(f"Qator {index + 1}: To'lov sanasi noto'g'ri formatda (YYYY-MM-DD HH:MM:SS)")

            try:
                payment_date = datetime.strptime(str(row[4]), '%Y-%m-%d %H:%M:%S')
                payment_date = timezone.make_aware(payment_date)  # <-- muhim o'zgarish
            except ValueError:
                raise ValidationError(f"Qator {index + 1}: To'lov sanasi noto'g'ri formatda (YYYY-MM-DD HH:MM:SS)")

            # Talaba
            try:
                student = Student.objects.get(jshshir=str(row[0]).strip())
            except Student.DoesNotExist:
                raise ValidationError(f"Qator {index + 1}: JSHSHIR {row[0]} bo'yicha talaba topilmadi")

            # Dublikat to'lovni tekshirish
            payment_id = str(row[2]).strip()
            if Payment.objects.filter(payment_id=payment_id).exists():
                skipped_count += 1
                continue  # mavjud to‘lovni tashlab ketamiz

            # Yangi to'lov yaratish
            payment = Payment(
                student=student,
                contract_number=str(row[1]).strip(),
                payment_id=payment_id,
                amount=amount,
                payment_date=payment_date,
                purpose=str(row[5]).strip()
            )
            payment.full_clean()
            payment.save()
            created_count += 1

        return {
            'success': True,
            'created_count': float(created_count),
            'skipped_count': float(skipped_count),
            'message': f"Muvaffaqiyatli import qilindi: {created_count} ta yangi to'lov qo'shildi, "
                       f"{skipped_count} ta mavjud to'lov o'tkazib yuborildi"
        }


def import_phone_numbers_from_excel(file_path):
    """
    Excel fayldan telefon raqamlarini o'qib, studentlarni yangilaydi
    """
    try:
        # Excel faylni yuklash (birinchi qator sarlavha emas)
        df = pd.read_excel(file_path, header=None)

        errors = []
        updates = []
        found_count = 0
        not_found_count = 0

        # Avval bazadagi barcha JSHSHIRlarni olish
        existing_jshshirs = set(Student.objects.values_list('jshshir', flat=True))

        # Har bir qatorni tekshirish (1-qatordan boshlanadi, 0-index sarlavha)
        for index, row in df.iterrows():
            # 1-qatorni (index=0) o'tkazib yuboramiz - bu sarlavha qatori
            if index == 0:
                continue

            try:
                # Index bo'yicha ustunlarni olish
                jshshir = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None  # 1-ustun: JSHSHIR
                phone_number = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else None  # 4-ustun: Telefon raqami

                # Ma'lumotlarni tekshirish
                if not jshshir or jshshir == 'nan':
                    errors.append(f"{index + 1}-qator: JSHSHIR bo'sh yoki noto'g'ri format")
                    continue

                if not phone_number or phone_number == 'nan':
                    errors.append(f"{index + 1}-qator: Telefon raqami bo'sh (JSHSHIR: {jshshir})")
                    continue

                # JSHSHIR dan qo'shimcha belgilarni tozalash
                jshshir = clean_jshshir(jshshir)
                if not jshshir:
                    errors.append(f"{index + 1}-qator: JSHSHIR noto'g'ri format")
                    continue

                # Telefon raqamini formatlash
                phone_number = normalize_phone_number(phone_number)
                if not phone_number:
                    errors.append(f"{index + 1}-qator: Noto'g'ri telefon raqami formati (JSHSHIR: {jshshir})")
                    continue

                # JSHSHIR bazada mavjudligini tekshirish
                if jshshir not in existing_jshshirs:
                    not_found_count += 1
                    continue  # Bazada yo'q bo'lsa, o'tkazib yuboramiz

                # Studentni topish va yangilash
                try:
                    student = Student.objects.get(jshshir=jshshir)
                    student.phone_number = phone_number
                    updates.append(student)
                    found_count += 1
                except Student.DoesNotExist:
                    not_found_count += 1
                except Student.MultipleObjectsReturned:
                    errors.append(f"{index + 1}-qator: JSHSHIR '{jshshir}' bo'yicha bir nechta student topildi")

            except Exception as e:
                errors.append(f"{index + 1}-qator: Qayta ishlash xatosi - {str(e)}")
                continue

        # Agar xatoliklar bo'lsa, yangilamaymiz
        if errors:
            return False, errors

        # Barcha yangilanishlarni bir transactionda bajarish
        with transaction.atomic():
            Student.objects.bulk_update(updates, ['phone_number'])

        success_message = (
            f"{len(updates)} ta studentning telefon raqami yangilandi. "
            f"{not_found_count} ta JSHSHIR bazada topilmadi."
        )

        return True, success_message

    except Exception as e:
        return False, [f"Faylni qayta ishlashda xatosi: {str(e)}"]


def clean_jshshir(jshshir):
    """JSHSHIR dan qo'shimcha belgilarni tozalash"""
    if not jshshir:
        return None

    # Qo'shtirnoq, bosh joy va maxsus belgilarni olib tashlash
    jshshir = jshshir.replace('"', '').replace("'", "").replace("`", "").strip()
    jshshir = ''.join(filter(lambda x: x.isalnum(), jshshir))
    return jshshir


def normalize_phone_number(phone):
    """Telefon raqamini standart formatga keltirish"""
    if not phone:
        return None

    # Faqat raqamlarni saqlash
    phone = ''.join(filter(str.isdigit, str(phone)))

    # Qo'shimcha tozalash
    phone = phone.replace(' ', '').replace('-', '').replace('+', '')

    # Uzbekistan telefon raqamlari uchun formatlash
    if phone.startswith('998') and len(phone) == 12:
        return phone
    elif phone.startswith('8') and len(phone) == 11:
        return '998' + phone[1:]
    elif phone.startswith('9') and len(phone) == 9:
        return '998' + phone
    else:
        return None
