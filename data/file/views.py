import io
import os
import subprocess
import tempfile

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

        replacements = {
            "{full_name}": student.full_name,
            "{course}": student.course,
            "{faculty}": student.specialization.faculty.name,
            "{contract}": f"{student.contract.first().period_amount_dt}",
            "{jshshir}": student.jshshir,
            "{specialization}": student.specialization.name,
            "{education_type}": student.education_type,
            "{group}": student.group,
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
            for p in doc.paragraphs:
                for key, value in replacements.items():
                    if key in p.text:
                        p.text = p.text.replace(key, value)

                if "{qr}" in p.text:
                    p.text = p.text.replace("{qr}", "")
                    run = p.add_run()
                    run.add_picture(qr_stream, width=Inches(1.5))

            doc.save(tmp_docx.name)
            output_docx = tmp_docx.name

        # LibreOffice orqali PDF ga o‘tkazish
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", tempfile.gettempdir(),
            output_docx
        ], check=True)

        pdf_path = output_docx.replace(".docx", ".pdf")

        # DB ga faqat PDF saqlash
        with open(pdf_path, "rb") as f:
            contract = ContractFiles.objects.create(student=student)
            contract.file.save(f"contract_{student.id}.pdf", f)

        # Vaqtinchalik fayllarni o‘chirish
        os.remove(output_docx)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return FileResponse(
            contract.file.open("rb"),
            as_attachment=True,
            filename=f"contract_{student.id}.pdf"
        )
