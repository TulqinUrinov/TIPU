from rest_framework import serializers
from .models import Files


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ["id", "file", "created_at"]


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ["id", "file", "uploaded_by"]
        read_only_fields = ["id", "uploaded_by"]

    def create(self, validated_data):
        user = self.context["request"].admin_user
        validated_data["uploaded_by"] = user
        return super().create(validated_data)