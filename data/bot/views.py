import os
import mimetypes
import requests
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
        post = serializer.save()
        self.send_to_users(post)
        return post

    def send_to_users(self, post):
        BOT_TOKEN = os.environ.get("BOT_TOKEN")
        base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"

        for user in BotUser.objects.all():
            chat_id = user.chat_id
            if not chat_id:
                continue

            if post.file:
                file_path = post.file.path
                mime_type, _ = mimetypes.guess_type(file_path)

                with open(file_path, "rb") as f:
                    if mime_type and mime_type.startswith("image"):
                        files = {"photo": f}
                        data = {"chat_id": chat_id, "caption": post.message}
                        requests.post(f"{base_url}/sendPhoto", data=data, files=files)

                    elif mime_type and mime_type.startswith("video"):
                        files = {"video": f}
                        data = {"chat_id": chat_id, "caption": post.message}
                        requests.post(f"{base_url}/sendVideo", data=data, files=files)

                    else:
                        files = {"document": f}
                        data = {"chat_id": chat_id, "caption": post.message}
                        requests.post(f"{base_url}/sendDocument", data=data, files=files)

            else:
                data = {"chat_id": chat_id, "text": post.message, "parse_mode": "HTML"}
                requests.post(f"{base_url}/sendMessage", data=data)

    @action(detail=True, methods=["post"])
    def resend(self, request, pk=None):
        """
        Oldin yaratilgan postni qayta yuborish
        """
        post = get_object_or_404(TgPost, pk=pk)
        self.send_to_users(post)
        return Response({"status": "success", "message": f"Post #{post.id} qayta yuborildi"})

# class TgPostViewSet(viewsets.ModelViewSet):
#     queryset = TgPost.objects.all().order_by("-created_at")
#     serializer_class = TgPostSerializer
#
#     def perform_create(self, serializer):
#         post = serializer.save()
#
#         BOT_TOKEN = os.environ.get("BOT_TOKEN")
#         base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
#
#         for user in BotUser.objects.all():
#             chat_id = user.chat_id
#             if not chat_id:
#                 continue
#
#             if post.file:
#                 file_path = post.file.path
#                 mime_type, _ = mimetypes.guess_type(file_path)
#
#                 with open(file_path, "rb") as f:
#                     if mime_type and mime_type.startswith("image"):
#                         # Rasm yuborish
#                         files = {"photo": f}
#                         data = {"chat_id": chat_id, "caption": post.message}
#                         requests.post(f"{base_url}/sendPhoto", data=data, files=files)
#
#                     elif mime_type and mime_type.startswith("video"):
#                         # Video yuborish
#                         files = {"video": f}
#                         data = {"chat_id": chat_id, "caption": post.message}
#                         requests.post(f"{base_url}/sendVideo", data=data, files=files)
#
#                     else:
#                         # Oddiy hujjat yuborish
#                         files = {"document": f}
#                         data = {"chat_id": chat_id, "caption": post.message}
#                         requests.post(f"{base_url}/sendDocument", data=data, files=files)
#
#             else:
#                 # Faqat matn yuboriladi
#                 data = {"chat_id": chat_id, "text": post.message, "parse_mode": "HTML"}
#                 requests.post(f"{base_url}/sendMessage", data=data)
#
#         return post
