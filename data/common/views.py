from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import tempfile
import os
from data.common.import_excel import import_students_from_excel, import_payments_from_excel, \
    import_phone_numbers_from_excel
from data.common.permission import IsAuthenticatedUserType


class ImportStudentsAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def post(self, request):
        if 'excel_file' not in request.FILES:
            return Response(
                {'error': 'Excel fayl yuklanmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'education_year' not in request.POST:
            return Response(
                {'error': 'education_year yuborilmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        excel_file = request.FILES['excel_file']
        education_year = request.POST.get('education_year')

        # Vaqtincha fayl yaratish
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in excel_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            # Import qilish
            result = import_students_from_excel(tmp_file_path, education_year)

            # Vaqtincha faylni o'chirish
            os.unlink(tmp_file_path)

            if result['success']:
                return Response(
                    {
                        'success': True,
                        'message': result['message'],
                        'created_count': result['created_count']
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'success': False,
                        'error': result['message']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            # Agar fayl mavjud bo'lsa, o'chirish
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

            return Response(
                {'error': f'Import jarayonida xato: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImportPaymentsAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def post(self, request):
        if 'excel_file' not in request.FILES:
            return Response(
                {'error': 'Excel fayl yuklanmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        excel_file = request.FILES['excel_file']

        # Vaqtincha fayl yaratish
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in excel_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        # try:
        # Import qilish
        result = import_payments_from_excel(tmp_file_path)

        # Vaqtincha faylni o'chirish
        os.unlink(tmp_file_path)

        if result['success']:
            return Response(
                {
                    'success': True,
                    'message': result['message'],
                    'created_count': result['created_count']
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': result['message']
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class StudentPhoneUploadAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def post(self, request):
        """
        Excel fayl orqali studentlarning telefon raqamlarini yangilash
        """

        if 'excel_file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'Excel fayl yuklanmadi'
            }, status=status.HTTP_400_BAD_REQUEST)

        excel_file = request.FILES['excel_file']

        # Fayl turini tekshirish
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            return Response({
                'success': False,
                'error': 'Faqat .xlsx yoki .xls formatidagi fayllar qabul qilinadi'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Faylni vaqtincha saqlash
        with open('temp_upload.xlsx', 'wb+') as destination:
            for chunk in excel_file.chunks():
                destination.write(chunk)

        # Import qilish
        success, result = import_phone_numbers_from_excel('temp_upload.xlsx')

        if success:
            return Response({
                'success': True,
                'message': result,
                'updated_count': int(result.split()[0])
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'errors': result,
                'error_count': len(result)
            }, status=status.HTTP_400_BAD_REQUEST)
