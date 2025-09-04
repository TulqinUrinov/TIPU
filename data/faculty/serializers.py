from rest_framework import serializers
from data.faculty.models import Faculty
from data.specialization.models import Specialization


class FacultySpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ("id", "code", "name")


class FacultySerializer(serializers.ModelSerializer):
    # POST/PUT paytida specialization’larni faqat ID orqali yuboramiz
    specialization_ids = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    # GET paytida specialization’larni to‘liq ko‘rsatamiz
    specializations = FacultySpecializationSerializer(many=True, read_only=True)

    class Meta:
        model = Faculty
        fields = ("id", "name", "specializations", "specialization_ids")

    def create(self, validated_data):
        specialization_ids = validated_data.pop("specialization_ids", [])
        faculty = Faculty.objects.create(**validated_data)

        # ManyToOne emas, ForeignKey bo‘lsa → specializationlarni update qilish kerak
        for specialization in specialization_ids:
            specialization.faculty = faculty
            specialization.save()

        return faculty

    def update(self, instance, validated_data):
        specialization_objs = validated_data.pop("specialization_ids", None)

        instance.name = validated_data.get("name", instance.name)
        instance.save()

        if specialization_objs is not None:
            # faqat kelgan specializationlarni facultyga bog‘laymiz
            for spec in specialization_objs:
                spec.faculty = instance
                spec.save()

        return instance

    # def update(self, instance, validated_data):
    #     specialization_ids = validated_data.pop("specialization_ids", None)
    #
    #     instance.name = validated_data.get("name", instance.name)
    #     instance.save()
    #
    #     if specialization_ids is not None:
    #         # avval eski specialization’larni faculty’dan uzib tashlaymiz
    #         instance.specializations.update(faculty=None)
    #
    #         for specialization in specialization_ids:
    #             specialization.faculty = instance
    #             specialization.save()
    #
    #     return instance
