from django.core.management import BaseCommand

from tg_bot.main import Bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Bot ishga tushdi!!!")
        bot = Bot()
        bot.run()
