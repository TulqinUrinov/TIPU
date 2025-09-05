from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from data.student.models import Student
from .models import StudentUser, SmsVerification


class SendSmsCodeSerializer(serializers.Serializer):
    jshshir = serializers.CharField(max_length=14)
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        jshshir = attrs.get("jshshir")
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        # parol tekshiruv
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Parollar mos emas"})

        # telefon raqam tekshiruvi
        if StudentUser.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError(
                {"phone_number": "Bu telefon raqami bilan allaqachon ro'yxatdan o'tilgan"})

        # student mavjudligi
        if not Student.objects.filter(jshshir=jshshir).exists():
            raise serializers.ValidationError({"jshshir": "Bunday JSHSHIR topilmadi"})

        return attrs

    def create(self, validated_data):
        phone_number = validated_data["phone_number"]
        jshshir = validated_data["jshshir"]
        password = make_password(validated_data["password"])

        # eski sms yozuvlarini o‘chiramiz
        SmsVerification.objects.filter(phone_number=phone_number, is_verified=False).delete()

        # yangi sms yozuv
        sms = SmsVerification.objects.create(
            phone_number=phone_number,
            jshshir=jshshir,
            password=password
        )
        return sms


class VerifySmsSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        code = attrs.get("code")

        try:
            sms = SmsVerification.objects.get(phone_number=phone_number, code=code, is_verified=False)
        except SmsVerification.DoesNotExist:
            raise serializers.ValidationError({"code": "Kod yoki telefon raqami noto‘g‘ri"})

        if sms.is_expired():
            raise serializers.ValidationError({"code": "Kod eskirgan"})

        attrs["sms"] = sms
        return attrs

    def create(self, validated_data):
        sms = validated_data["sms"]

        # studentni topamiz
        student = Student.objects.get(jshshir=sms.jshshir)

        # StudentUser yaratamiz
        user = StudentUser.objects.create(
            student=student,
            phone_number=sms.phone_number,
            password=sms.password  # hashlangan holda saqlangan
        )

        # smsni tasdiqlash
        sms.is_verified = True
        sms.save()

        return user


# Login
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


# Parolni yangilash
class StudentUserPasswordUpdateSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Parollar mos emas")
        return attrs

    def save(self, **kwargs):
        student_user = self.context['request'].student_user
        student_user.set_password(self.validated_data['new_password'])
        return student_user

# # Registratsiya
# class StudentUserRegisterSerializer(serializers.ModelSerializer):
#     jshshir = serializers.CharField(write_only=True)
#     password = serializers.CharField(write_only=True)
#     confirm_password = serializers.CharField(write_only=True)
#
#     class Meta:
#         model = StudentUser
#         fields = ('jshshir', 'phone_number', 'password', 'confirm_password')
#
#     def validate(self, attrs):
#         if attrs['password'] != attrs['confirm_password']:
#             raise serializers.ValidationError("Parollar mos kelmadi")
#
#         # JSHSHIR orqali studentni topish
#         try:
#             student = Student.objects.get(jshshir=attrs['jshshir'])
#         except Student.DoesNotExist:
#             raise serializers.ValidationError("Bunday JSHSHIR bilan talaba topilmadi")
#
#         # Telefon raqam unikal ligini tekshirish
#         if StudentUser.objects.filter(phone_number=attrs['phone_number']).exists():
#             raise serializers.ValidationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan")
#
#         attrs['student'] = student
#         return attrs
#
#     def create(self, validated_data):
#         student = validated_data['student']
#
#         user = StudentUser.objects.create(
#             student=student,
#             phone_number=validated_data['phone_number']
#         )
#         # Parolni hash qilish
#         user.set_password(validated_data['password'])
#         return user
