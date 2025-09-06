from rest_framework import serializers
from .models import Files, FileDeleteHistory


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

        def validate(self, attrs):
            file_type = attrs.get("file_type")

            if file_type in ["MUQOBIL", "HEMIS"]:
                qs = Files.objects.filter(file_type=file_type)
                if self.instance:  # update paytida
                    qs = qs.exclude(pk=self.instance.pk)

                if qs.exists():
                    raise serializers.ValidationError(
                        {"file_type": f"{file_type} hujjati allaqachon mavjud."}
                    )
            return attrs

    def create(self, validated_data):
        user = self.context["request"].admin_user
        validated_data["uploaded_by"] = user
        return super().create(validated_data)


# O'chirilgan excel filelar tarixi
class FileDeleteHistorySerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source="file.file.name", read_only=True)  # fayl nomi
    file_url = serializers.SerializerMethodField()  # fayl url
    deleted_by = serializers.CharField(source="deleted_by.full_name", read_only=True)  # o‘chirgan odam

    class Meta:
        model = FileDeleteHistory
        fields = [
            "id",
            "file",
            "file_name",
            "file_url",
            "deleted_by",
            "reason",
        ]

    def get_file_url(self, obj):
        if obj.file and obj.file.file:
            return obj.file.file.url
        return None
