from rest_framework import serializers

from data.education_year.models import EducationYear


class EducationYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationYear
        fields = ("id", "year")
