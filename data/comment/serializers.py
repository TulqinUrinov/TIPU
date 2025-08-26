from rest_framework import serializers

from data.comment.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'student', 'student_name', 'user', 'user_name', 'message', 'created_at']
        read_only_fields = ['user', 'created_at']
