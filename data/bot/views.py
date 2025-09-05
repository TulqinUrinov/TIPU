from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from data.bot.models import TgPost, BotUser
from data.bot.serializers import TgPostSerializer
from data.common.permission import IsAuthenticatedUserType


class TgPostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedUserType]
    queryset = TgPost.objects.all().order_by("-created_at")
    serializer_class = TgPostSerializer

    def perform_create(self, serializer):
        from data.bot.tasks import send_post_task
        post = serializer.save()
        if post.scheduled_time:
            send_post_task.apply_async((post.id,), eta=post.scheduled_time)
        return post

    @action(detail=True, methods=["post"])
    def resend(self, request, pk=None):
        """
        Oldin yaratilgan postni qayta yuborish
        """
        post = get_object_or_404(TgPost, pk=pk)
        self.send_to_users(post)
        return Response({"status": "success", "message": f"Post #{post.id} qayta yuborildi"})
