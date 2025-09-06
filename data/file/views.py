from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework import generics, views, viewsets, status
from rest_framework.generics import ListAPIView

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from data.common.permission import IsAuthenticatedUserType
from data.file.generate import generate_contract
from data.file.models import Files, FileDeleteHistory
from data.file.serializers import FileSerializer, FileUploadSerializer, FileDeleteHistorySerializer

from data.student.models import Student


class ImportHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticatedUserType]
    queryset = Files.objects.filter(is_archived=False).order_by("-created_at")
    serializer_class = FileSerializer


# Barcha Filelar
class FileViewSet(viewsets.ModelViewSet):
    queryset = Files.objects.filter(is_archived=False)
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticatedUserType]


# faqat shablon
class SpecialDocsListApiView(generics.ListAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self):
        return Files.objects.filter(file_type__in=["MUQOBIL", "HEMIS"])


class ContractDownloadApiView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        contract_file = generate_contract(student)
        return FileResponse(
            contract_file.file.open("rb"),
            as_attachment=True,
            filename=f"contract_{student.id}.pdf"
        )


# O'chirilgan excel filelar tarixi
class FileDeleteHistoryListAPIView(ListAPIView):
    permission_classes = [IsAuthenticatedUserType]
    queryset = FileDeleteHistory.objects.all()
    serializer_class = FileDeleteHistorySerializer


class FileDeleteAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def post(self, request, file_id):
        try:
            file_obj = Files.objects.get(id=file_id)
        except Files.DoesNotExist:
            return Response(
                {"error": "File topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        reason = request.data.get('reason', '')

        with transaction.atomic():
            # Ma'lumotlarni sanab olish
            deleted_data_count = {
                'students': file_obj.students.count(),
                'phone_students': file_obj.phone_students.count(),
                'contracts': file_obj.contracts.count(),
                'payments': file_obj.payments.count(),
                'specializations': file_obj.specializations.count(),
                'faculties': file_obj.faculties.count()
            }

            # Ma'lumotlarni o'chirish
            file_obj.payments.all().delete()
            file_obj.contracts.all().delete()

            # Asosiy studentlarni o'chirish
            for student in file_obj.students.all():
                if student.payments.exists() or student.contract.exists():
                    student.source_file = None
                    student.save()
                else:
                    student.delete()

            # Telefon raqami yangilangan studentlarni qaytarish
            for student in file_obj.phone_students.all():
                student.phone_number = None
                student.phone_source_file = None
                student.save()

            # Mutaxassisliklarni o'chirish (boshqa fayllardan kelganlarni saqlab qolish)
            for specialization in file_obj.specializations.all():
                if specialization.students.exists():
                    specialization.source_file = None
                    specialization.save()
                else:
                    specialization.delete()

            # Fakultetlarni o'chirish (boshqa fayllardan kelganlarni saqlab qolish)
            for faculty in file_obj.faculties.all():
                if faculty.specializations.exists():
                    faculty.source_file = None
                    faculty.save()
                else:
                    faculty.delete()

            # History yozish
            FileDeleteHistory.objects.create(
                file=file_obj,
                deleted_by=request.admin_user,
                deleted_data_count=deleted_data_count,
                reason=reason
            )

            # Faylni o'chirish (soft delete)
            file_obj.soft_delete()

        return Response({
            "success": True,
            "message": "File va tegishli ma'lumotlar o'chirildi",
            "deleted_data_count": deleted_data_count
        }, status=status.HTTP_200_OK)

# # Yuklangan excel filelardagi ma'lumotlarni o'chirish
# class FileDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticatedUserType]
#
#     def post(self, request, file_id):
#         try:
#             file_obj = Files.objects.get(id=file_id)
#         except Files.DoesNotExist:
#             return Response(
#                 {"error": "File topilmadi"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         reason = request.data.get('reason', '')
#
#         with transaction.atomic():
#             # Ma'lumotlarni sanab olish
#             deleted_data_count = {
#                 'students': file_obj.students.count(),
#                 'contracts': file_obj.contracts.count(),
#                 'payments': file_obj.payments.count(),
#                 'specializations': file_obj.specializations.count(),
#                 'faculties': file_obj.faculties.count()
#             }
#
#             # Ma'lumotlarni o'chirish
#             file_obj.payments.all().delete()
#             file_obj.contracts.all().delete()
#
#             # Studentlarni o'chirish (boshqa fayllardan kelgan studentlarni saqlab qolish)
#             for student in file_obj.students.all():
#                 # Agar student boshqa fayllarga ham bog'langan bo'lsa, source_file ni null qilish
#                 if student.payments.exists() or student.contract.exists():
#                     student.source_file = None
#                     student.save()
#                 else:
#                     # Agar faqat shu faylga bog'langan bo'lsa, o'chirish
#                     student.delete()
#
#             # Mutaxassisliklarni o'chirish (boshqa fayllardan kelganlarni saqlab qolish)
#             for specialization in file_obj.specializations.all():
#                 if specialization.students.exists():
#                     specialization.source_file = None
#                     specialization.save()
#                 else:
#                     specialization.delete()
#
#             # Fakultetlarni o'chirish (boshqa fayllardan kelganlarni saqlab qolish)
#             for faculty in file_obj.faculties.all():
#                 if faculty.specializations.exists():
#                     faculty.source_file = None
#                     faculty.save()
#                 else:
#                     faculty.delete()
#
#             # History yozish
#             FileDeleteHistory.objects.create(
#                 file=file_obj,
#                 deleted_by=request.admin_user,
#                 deleted_data_count=deleted_data_count,
#                 reason=reason
#             )
#
#             # Faylni o'chirish (soft delete)
#             file_obj.soft_delete()
#
#         return Response({
#             "success": True,
#             "message": "File va tegishli ma'lumotlar o'chirildi",
#             "deleted_data_count": deleted_data_count
#         }, status=status.HTTP_200_OK)
#
