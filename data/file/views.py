import io
import os
import subprocess

from django.conf import settings
from django.http import FileResponse, Http404

from rest_framework import generics, views
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


class FileUploadApiView(generics.CreateAPIView):
    """Admin DOCX fayl yuklashi uchun API"""

    queryset = Files.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticatedUserType]


class ContractDownloadApiView(views.APIView):
    """Shartnomani PDF shaklida yuklab beruvchi API"""

    permission_classes = [IsAuthenticatedUserType]

    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            raise Http404("Student not found")

        # Agar allaqachon shartnomasi bo‘lsa → uni qaytarish
        existing_contract = ContractFiles.objects.filter(student=student).first()
        if existing_contract:
            return FileResponse(
                existing_contract.file.open("rb"),
                as_attachment=True,
                filename=os.path.basename(existing_contract.file.name)
            )

        # Student turini aniqlash
        if hasattr(student, "user_account"):  # muqobil to'lov talaba
            template_type = "MUQOBIL"
        else:
            template_type = "HEMIS"

        # Mos shablonni olish
        try:
            file = Files.objects.get(file_type=template_type)
        except Files.DoesNotExist:
            raise Http404(f"{template_type} shablon topilmadi")

        # Student ma’lumotlarini qo‘yish
        replacements = {
            "{full_name}": student.full_name,
            "{course}": student.course,
            "{faculty}": student.specialization.name,
            "{contract}": f"{student.contract.first().period_amount_dt}",
        }

        input_path = file.file.path
        output_docx = os.path.join(settings.MEDIA_ROOT, f"temp_{student.id}.docx")

        # QR kod (saqlangan PDF manzili bo‘ladi)
        qr_url = f"{settings.SITE_URL}/contracts/{student.id}/download/"
        qr_img = qrcode.make(qr_url)
        qr_stream = io.BytesIO()
        qr_img.save(qr_stream, format='PNG')
        qr_stream.seek(0)

        # DOCX ni ochib o‘zgartirish
        doc = Document(input_path)
        for p in doc.paragraphs:
            for key, value in replacements.items():
                if key in p.text:
                    p.text = p.text.replace(key, value)

            if "{qr}" in p.text:
                p.text = p.text.replace("{qr}", "")
                run = p.add_run()
                run.add_picture(qr_stream, width=Inches(1.5))

        doc.save(output_docx)

        # LibreOffice orqali PDF ga o‘tkazish
        output_pdf_dir = settings.MEDIA_ROOT
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_pdf_dir,
            output_docx
        ], check=True)

        pdf_path = output_docx.replace(".docx", ".pdf")

        # Shartnomani DB ga saqlash
        with open(pdf_path, "rb") as f:
            contract = ContractFiles.objects.create(
                student=student,
            )
            contract.file.save(f"contract_{student.id}.pdf", f)

        return FileResponse(
            open(pdf_path, "rb"),
            as_attachment=True,
            filename=os.path.basename(pdf_path)
        )

# class ContractDownloadApiView(views.APIView):
#     """Shartnomani PDF shaklida yuklab beruvchi API"""
#
#     permission_classes = [IsAuthenticatedUserType]
#
#     def get(self, request, pk):
#         try:
#             file = Files.objects.get(pk=pk)
#         except Files.DoesNotExist:
#             raise Http404("File not found")
#
#         replacements = {
#             "{full_name}": "Ali Valiyev",
#             "{course}": "3-kurs",
#             "{faculty}": "Informatika fakulteti",
#             "{contract}": "123456",
#         }
#
#         # DOCX fayl manzili va vaqtinchalik chiqish fayli
#         input_path = file.file.path
#         output_docx = os.path.join(settings.MEDIA_ROOT, f"temp_{file.id}.docx")
#
#         # QR kodni in-memory yaratish
#         qr_url = f"{settings.SITE_URL}/files/{file.id}/download/"
#         qr_img = qrcode.make(qr_url)
#         qr_stream = io.BytesIO()
#         qr_img.save(qr_stream, format='PNG')
#         qr_stream.seek(0)
#
#         # DOCX ochish va keywordlarni almashtirish
#         doc = Document(input_path)
#
#         for p in doc.paragraphs:
#             for key, value in replacements.items():
#                 if key in p.text:
#                     p.text = p.text.replace(key, value)
#
#             if "{qr}" in p.text:
#                 p.text = p.text.replace("{qr}", "")
#                 run = p.add_run()
#                 run.add_picture(qr_stream, width=Inches(1.5))
#
#         doc.save(output_docx)
#
#         # LibreOffice orqali PDF ga o‘tkazish
#         output_pdf_dir = settings.MEDIA_ROOT
#         subprocess.run([
#             "libreoffice",
#             "--headless",
#             "--convert-to", "pdf",
#             "--outdir", output_pdf_dir,
#             output_docx
#         ], check=True)
#
#         pdf_path = output_docx.replace(".docx", ".pdf")
#
#         return FileResponse(
#             open(pdf_path, "rb"),
#             as_attachment=True,
#             filename=os.path.basename(pdf_path)
#         )
#
#
