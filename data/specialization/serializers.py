from rest_framework import serializers

from data.specialization.models import Specialization


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = [
            "id",
            "name",
            "code",
        ]
