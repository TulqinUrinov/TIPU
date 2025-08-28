from rest_framework.generics import ListAPIView
from data.common.permission import IsAuthenticatedUserType
from data.file.models import Files
from data.file.serializers import FileSerializer, FileUploadSerializer
import os
import qrcode
import subprocess
from django.http import FileResponse, Http404
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from docx import Document
from docx.shared import Inches


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
            file = Files.objects.get(pk=pk)
        except Files.DoesNotExist:
            raise Http404("File not found")

        replacements = {
            "{full_name}": "Ali Valiyev",
            "{course}": "3-kurs",
            "{faculty}": "Informatika fakulteti",
            "{contract}": "123456",
        }

        # QR link yaratish
        qr_url = f"{settings.SITE_URL}/files/{file.id}/download/"
        qr_img_path = os.path.join(settings.MEDIA_ROOT, f"qr_{file.id}.png")
        qr_img = qrcode.make(qr_url)
        qr_img.save(qr_img_path)

        # DOCX ochish va keywordlarni almashtirish
        input_path = file.file.path
        output_docx = os.path.join(settings.MEDIA_ROOT, f"temp_{file.id}.docx")

        doc = Document(input_path)

        for p in doc.paragraphs:
            for key, value in replacements.items():
                if key in p.text:
                    p.text = p.text.replace(key, value)

            if "{qr}" in p.text:
                p.text = p.text.replace("{qr}", "")
                run = p.add_run()
                run.add_picture(qr_img_path, width=Inches(1.5))

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

        return FileResponse(open(pdf_path, "rb"), as_attachment=True, filename=os.path.basename(pdf_path))
