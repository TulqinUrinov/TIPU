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

    # def validate(self, attrs):
    #     file_type = attrs.get("file_type")
    #     if file_type in ["MUQOBIL", "HEMIS"]:
    #         if Files.objects.filter(file_type=file_type).exists():
    #             raise serializers.ValidationError(
    #                 { "file_type": f"{file_type} hujjati allaqachon mavjud." }
    #             )
    #     return attrs

    def create(self, validated_data):
        user = self.context["request"].admin_user
        validated_data["uploaded_by"] = user
        return super().create(validated_data)
