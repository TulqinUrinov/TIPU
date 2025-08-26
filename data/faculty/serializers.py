from rest_framework import serializers

from data.faculty.models import Faculty


class FacultySeriazlizer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = (
            'id',
            'name',
        )
