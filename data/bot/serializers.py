from rest_framework import serializers

from data.bot.models import TgPost


class TgPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgPost
        fields = [
            'id',
            "message",
            "file",
        ]
