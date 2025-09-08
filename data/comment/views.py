from rest_framework import generics
from .models import Comment
from .serializers import CommentSerializer
from data.common.permission import IsAuthenticatedUserType


class CommentCreateAPIView(generics.CreateAPIView):
    """Admin tomonidan Studentga comment qoldirish"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedUserType]

    def perform_create(self, serializer):
        # Avtomatik ravishda joriy foydalanuvchini (adminni) saqlaymiz
        serializer.save(user=self.request.admin_user)


class StudentCommentsListAPIView(generics.ListAPIView):
    """Studentga qoldirilgan barcha commentlarni olish"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return Comment.objects.filter(student_id=student_id).select_related('user', 'student').order_by('created_at')
