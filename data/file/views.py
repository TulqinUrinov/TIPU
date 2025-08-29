import io
import os
import subprocess
import tempfile

from django.conf import settings
from django.http import FileResponse, Http404

from rest_framework import generics, views, viewsets
from rest_framework.generics import ListAPIView

from docx import Document
from docx.shared import Inches

import qrcode

from data.common.permission import IsAuthenticatedUserType
from data.file.models import Files, ContractFiles
from data.file.serializers import FileSerializer, FileUploadSerializer
from data.student.models import Student


class ImportHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticatedUserType]
    queryset = Files.objects.all().order_by("-created_at")
    serializer_class = FileSerializer

# Barcha Filelar
class FileViewSet(viewsets.ModelViewSet):
    queryset = Files.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticatedUserType]

# faqat shablon
class SpecialDocsListApiView(generics.ListAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self):
        return Files.objects.filter(file_type__in=["MUQOBIL", "HEMIS"])

class ContractDownloadApiView(views.APIView):
    """Shartnomani PDF shaklida yuklab beruvchi API"""
    permission_classes = [IsAuthenticatedUserType]

    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            raise Http404("Student not found")

        # Avval DB dan mavjud shartnomani topamiz
        existing_contract = ContractFiles.objects.filter(student=student).first()

        # Agar mavjud bo'lsa va fayl mavjud bo'lsa → qaytarish
        if existing_contract and existing_contract.file and os.path.exists(existing_contract.file.path):
            return FileResponse(
                existing_contract.file.open("rb"),
                as_attachment=True,
                filename=os.path.basename(existing_contract.file.name)
            )

        # Student turini aniqlash
        template_type = "MUQOBIL" if hasattr(student, "user_account") else "HEMIS"

        # Shablonni olish
        try:
            file = Files.objects.get(file_type=template_type)
        except Files.DoesNotExist:
            raise Http404(f"{template_type} shablon topilmadi")

        contract = student.contract.first()

        # To'ldirish uchun ma'lumotlar
        replacements = {
            "{filial}": "Bosh filial",  # Kerak bo'lsa, student ma'lumotlaridan oling
            "{name}": str(student.full_name),
            "{mode}": str(student.education_form),
            "{delta}": str(5 if student.education_form == "Sirtqi" else 4),
            "{course}": str(student.course),
            "{faculty}": str(student.specialization.name),
            "{price}": str(contract.period_amount_dt) if contract else "",
            "{jshir}": str(student.jshshir),
            "{phone}": str(student.user_account.phone_number) if hasattr(student, "user_account") else str(
                student.phone_number or ""),
        }

        # QR kod yaratish
        qr_url = f"{settings.SITE_URL}/contracts/{student.id}/download/"
        qr_img = qrcode.make(qr_url)
        qr_stream = io.BytesIO()
        qr_img.save(qr_stream, format="PNG")
        qr_stream.seek(0)

        # Vaqtinchalik docx yaratish
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
            doc = Document(file.file.path)

            # Paragraphlardagi kalit so'zlarni almashtirish (formatni saqlab qolgan holda)
            for paragraph in doc.paragraphs:
                self.replace_text_preserving_format(paragraph, replacements)

            # Jadvaldagi kalit so'zlarni almashtirish (formatni saqlab qolgan holda)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            self.replace_text_preserving_format(paragraph, replacements)

            # QR kod qo'shish
            for paragraph in doc.paragraphs:
                if "{qr}" in paragraph.text:
                    # {qr} ni olib tashlash
                    paragraph.text = paragraph.text.replace("{qr}", "")
                    # QR kodni qo'shish
                    run = paragraph.add_run()
                    run.add_picture(qr_stream, width=Inches(1.5))

            doc.save(tmp_docx.name)
            output_docx = tmp_docx.name

        # LibreOffice orqali PDF ga o'tkazish
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", tempfile.gettempdir(),
            output_docx
        ], check=True)

        pdf_path = output_docx.replace(".docx", ".pdf")

        # DB ga PDF saqlash
        with open(pdf_path, "rb") as f:
            contract_file = ContractFiles.objects.create(student=student)
            contract_file.file.save(f"contract_{student.id}.pdf", f)

        # Vaqtinchalik fayllarni o'chirish
        os.remove(output_docx)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return FileResponse(
            contract_file.file.open("rb"),
            as_attachment=True,
            filename=f"contract_{student.id}.pdf"
        )

    def replace_text_preserving_format(self, paragraph, replacements):
        """Formatlashni saqlab qolgan holda matnni almashtirish"""
        # Paragraphdagi barcha runlarni tekshiramiz
        for run in paragraph.runs:
            original_text = run.text
            new_text = original_text

            # Har bir kalit so'zni almashtiramiz
            for key, value in replacements.items():
                if key in new_text:
                    new_text = new_text.replace(key, value)

            # Agar matn o'zgarganga, runni yangilaymiz
            if new_text != original_text:
                run.text = new_text








# class ContractDownloadApiView(views.APIView):
#     """Shartnomani PDF shaklida yuklab beruvchi API"""
#     permission_classes = [IsAuthenticatedUserType]
#
#     def get(self, request, pk):
#         try:
#             student = Student.objects.get(pk=pk)
#         except Student.DoesNotExist:
#             raise Http404("Student not found")
#
#         # Avval DB dan mavjud shartnomani topamiz
#         existing_contract = ContractFiles.objects.filter(student=student).first()
#
#         # Agar mavjud bo'lsa va fayl mavjud bo'lsa → qaytarish
#         if existing_contract and existing_contract.file and os.path.exists(existing_contract.file.path):
#             return FileResponse(
#                 existing_contract.file.open("rb"),
#                 as_attachment=True,
#                 filename=os.path.basename(existing_contract.file.name)
#             )
#
#         # Student turini aniqlash
#         template_type = "MUQOBIL" if hasattr(student, "user_account") else "HEMIS"
#
#         # Shablonni olish
#         try:
#             file = Files.objects.get(file_type=template_type)
#         except Files.DoesNotExist:
#             raise Http404(f"{template_type} shablon topilmadi")
#
#         contract = student.contract.first()
#
#         # To'ldirish uchun ma'lumotlar
#         replacements = {
#             "{filial}": "Bosh filial",  # Kerak bo'lsa, student ma'lumotlaridan oling
#             "{name}": str(student.full_name),
#             "{mode}": str(student.education_form),
#             "{delta}": str(5 if student.education_form == "Sirtqi" else 4),
#             "{course}": str(student.course),
#             "{faculty}": str(student.specialization.name),
#             "{price}": str(contract.period_amount_dt) if contract else "",
#             # "{birthplace}": str(student.birth_place or ""),
#             # "{passport}": str(student.passport_data or ""),
#             "{jshir}": str(student.jshshir),
#             "{phone}": str(student.user_account.phone_number) if hasattr(student, "user_account") else str(
#                 student.phone_number or ""),
#         }
#
#         # QR kod yaratish
#         qr_url = f"{settings.SITE_URL}/contracts/{student.id}/download/"
#         qr_img = qrcode.make(qr_url)
#         qr_stream = io.BytesIO()
#         qr_img.save(qr_stream, format="PNG")
#         qr_stream.seek(0)
#
#         # Vaqtinchalik docx yaratish
#         with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
#             doc = Document(file.file.path)
#
#             # Paragraphlardagi kalit so'zlarni almashtirish
#             for paragraph in doc.paragraphs:
#                 for key, value in replacements.items():
#                     if key in paragraph.text:
#                         paragraph.text = paragraph.text.replace(key, value)
#
#             # Jadvaldagi kalit so'zlarni almashtirish
#             for table in doc.tables:
#                 for row in table.rows:
#                     for cell in row.cells:
#                         for paragraph in cell.paragraphs:
#                             for key, value in replacements.items():
#                                 if key in paragraph.text:
#                                     paragraph.text = paragraph.text.replace(key, value)
#
#             # QR kod qo'shish
#             for paragraph in doc.paragraphs:
#                 if "{qr}" in paragraph.text:
#                     paragraph.text = paragraph.text.replace("{qr}", "")
#                     run = paragraph.add_run()
#                     run.add_picture(qr_stream, width=Inches(1.5))
#
#             doc.save(tmp_docx.name)
#             output_docx = tmp_docx.name
#
#         # LibreOffice orqali PDF ga o'tkazish
#         subprocess.run([
#             "libreoffice",
#             "--headless",
#             "--convert-to", "pdf",
#             "--outdir", tempfile.gettempdir(),
#             output_docx
#         ], check=True)
#
#         pdf_path = output_docx.replace(".docx", ".pdf")
#
#         # DB ga PDF saqlash
#         with open(pdf_path, "rb") as f:
#             contract_file = ContractFiles.objects.create(student=student)
#             contract_file.file.save(f"contract_{student.id}.pdf", f)
#
#         # Vaqtinchalik fayllarni o'chirish
#         os.remove(output_docx)
#         if os.path.exists(pdf_path):
#             os.remove(pdf_path)
#
#         return FileResponse(
#             contract_file.file.open("rb"),
#             as_attachment=True,
#             filename=f"contract_{student.id}.pdf"
#         )

# class ContractDownloadApiView(views.APIView):
#     """Shartnomani PDF shaklida yuklab beruvchi API"""
#     permission_classes = [IsAuthenticatedUserType]
#
#     def get(self, request, pk):
#         try:
#             student = Student.objects.get(pk=pk)
#         except Student.DoesNotExist:
#             raise Http404("Student not found")
#
#         # Avval DB dan mavjud shartnomani topamiz
#         existing_contract = ContractFiles.objects.filter(student=student).first()
#
#         # Agar mavjud bo'lsa va fayl mavjud bo'lsa → qaytarish
#         if existing_contract and existing_contract.file and os.path.exists(existing_contract.file.path):
#             return FileResponse(
#                 existing_contract.file.open("rb"),
#                 as_attachment=True,
#                 filename=os.path.basename(existing_contract.file.name)
#             )
#
#         # Student turini aniqlash
#         template_type = "MUQOBIL" if hasattr(student, "user_account") else "HEMIS"
#
#         # Shablonni olish
#         try:
#             file = Files.objects.get(file_type=template_type)
#         except Files.DoesNotExist:
#             raise Http404(f"{template_type} shablon topilmadi")
#
#         contract = student.contract.first()
#
#         replacements = {
#             "{jshir}": str(student.jshshir),
#             "{name}": str(student.full_name),
#             "{delta}": str(5 if student.education_form == "Sirtqi" else 4),
#             "{course}": str(student.course),
#             "{faculty}": str(student.specialization.name),
#             "{price}": str(contract.period_amount_dt) if contract else "",
#             "{phone}": str(student.user_account.phone_number) if hasattr(student, "user_account") else str(
#                 student.phone_number or ""),
#             "{mode}": str(student.education_type),
#         }
#
#         # QR kod yaratish
#         qr_url = f"{settings.SITE_URL}/contracts/{student.id}/download/"
#         qr_img = qrcode.make(qr_url)
#         qr_stream = io.BytesIO()
#         qr_img.save(qr_stream, format="PNG")
#         qr_stream.seek(0)
#
#         # Vaqtinchalik docx yaratish
#         with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
#             doc = Document(file.file.path)
#             for p in doc.paragraphs:
#                 for key, value in replacements.items():
#                     if key in p.text:
#                         p.text = p.text.replace(key, value)
#                 if "{qr}" in p.text:
#                     p.text = p.text.replace("{qr}", "")
#                     run = p.add_run()
#                     run.add_picture(qr_stream, width=Inches(1.5))
#             doc.save(tmp_docx.name)
#             output_docx = tmp_docx.name
#
#         # LibreOffice orqali PDF ga o‘tkazish
#         subprocess.run([
#             "libreoffice",
#             "--headless",
#             "--convert-to", "pdf",
#             "--outdir", tempfile.gettempdir(),
#             output_docx
#         ], check=True)
#
#         pdf_path = output_docx.replace(".docx", ".pdf")
#
#         # DB ga PDF saqlash
#         with open(pdf_path, "rb") as f:
#             contract = ContractFiles.objects.create(student=student)
#             contract.file.save(f"contract_{student.id}.pdf", f)
#
#         # Vaqtinchalik fayllarni o‘chirish
#         os.remove(output_docx)
#         if os.path.exists(pdf_path):
#             os.remove(pdf_path)
#
#         return FileResponse(
#             contract.file.open("rb"),
#             as_attachment=True,
#             filename=f"contract_{student.id}.pdf"
#         )

