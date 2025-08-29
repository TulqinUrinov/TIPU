from rest_framework import serializers
from .models import Files


class FileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SerializerMethodField()
    class Meta:
        model = Files
        fields = ["id", "file_type", "file", "uploaded_by", "created_at"]

    def get_uploaded_by(self, obj: Files):
        return obj.uploaded_by.full_name if obj.uploaded_by else None


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ["id", "file_type", "file", "uploaded_by"]
        read_only_fields = ["id", "uploaded_by"]

    def create(self, validated_data):
        user = self.context["request"].admin_user
        validated_data["uploaded_by"] = user
        return super().create(validated_data)
