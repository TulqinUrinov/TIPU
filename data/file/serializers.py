from rest_framework import serializers
from .models import Files

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ["id", "file", "uploaded_by", "created_at"]