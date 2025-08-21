
from rest_framework import serializers

from data.account.models import StudentUser
from data.student.models import Student


class StudentUserRegisterSerializer(serializers.ModelSerializer):
    jshshir = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = StudentUser
        fields = ('jshshir', 'phone_number', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Parollar mos kelmadi")

        # JSHSHIR orqali studentni topish
        try:
            student = Student.objects.get(jshshir=attrs['jshshir'])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Bunday JSHSHIR bilan talaba topilmadi")

        # Telefon raqam unikal ligini tekshirish
        if StudentUser.objects.filter(phone_number=attrs['phone_number']).exists():
            raise serializers.ValidationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan")

        attrs['student'] = student
        return attrs

    def create(self, validated_data):
        student = validated_data['student']

        user = StudentUser.objects.create(
            student=student,
            phone_number=validated_data['phone_number']
        )
        # Parolni hash qilish
        user.set_password(validated_data['password'])
        return user


class StudentUserLoginSerializer(serializers.Serializer):
    jshshir = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        jshshir = attrs.get('jshshir')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        try:
            student_user = StudentUser.objects.get(
                student__jshshir=jshshir,
                phone_number=phone_number
            )
        except StudentUser.DoesNotExist:
            raise serializers.ValidationError('JSHSHIR, telefon raqam yoki parol noto‘g‘ri')

        if not student_user.check_password(password):
            raise serializers.ValidationError('JSHSHIR, telefon raqam yoki parol noto‘g‘ri')

        attrs['student_user'] = student_user
        return attrs
