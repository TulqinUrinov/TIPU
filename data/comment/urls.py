from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.CommentCreateAPIView.as_view(), name='comment-create'),
    path('student/<int:student_id>/', views.StudentCommentsListAPIView.as_view(), name='student-comments'),
]
