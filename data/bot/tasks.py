import mimetypes
import os

import requests
from celery import shared_task
from data.bot.models import TgPost, BotUser


@shared_task
def send_post_task(post_id):
    post = TgPost.objects.get(id=post_id, is_sent=False)
    send_to_users(post)
    post.is_sent = True
    post.save()


# Yaratilgan postni yuborish
def send_to_users(post):
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
