from rest_framework import serializers

from data.user.models import AdminUser


class AdminUserSerializer(serializers.ModelSerializer):
    # id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AdminUser
        fields = (
            'id',
            'full_name',
            'phone_number',
            'password',
            'is_archived',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_archived')

    def create(self, validated_data):
        # Parolni hash qilish
        password = validated_data.pop('password', None)
        user = AdminUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
        return user

    def update(self, instance, validated_data):
        # Parolni hash qilish
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AdminUserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        try:
            user = AdminUser.objects.get(phone_number=phone_number)
        except AdminUser.DoesNotExist:
            raise serializers.ValidationError('Telefon raqam yoki parol noto‘g‘ri')

        if not user.check_password(password):
            raise serializers.ValidationError('Telefon raqam yoki parol noto‘g‘ri')

        if getattr(user, "is_archived", False):
            raise serializers.ValidationError('Hisobingiz bloklangan')

        attrs['user'] = user
        return attrs


