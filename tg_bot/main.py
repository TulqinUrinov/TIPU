import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from data.student.models import Student
from data.bot.models import BotUser

ASK_JSHSHIR = 1  # Conversation state

class Bot:

    def __init__(self):
        BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()

        # Conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                ASK_JSHSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_jshshir)]
            },
            fallbacks=[]
        )

        self.app.add_handler(conv_handler)

    def run(self):
        self.app.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Passport JSHSHIR raqamingizni kiriting:"
        )
        return ASK_JSHSHIR

    async def ask_jshshir(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        jshshir_input = update.message.text.strip()

        try:
            student = Student.objects.get(jshshir=jshshir_input)
        except Student.DoesNotExist:
            await update.message.reply_text("Bunday JSHSHIR topilmadi. Iltimos, qayta kiriting:")
            return ASK_JSHSHIR

        # BotUser yaratish yoki yangilash
        bot_user, created = BotUser.objects.get_or_create(
            chat_id=update.effective_chat.id,
            defaults={
                "username": update.effective_user.username,
                "tg_name": update.effective_user.full_name,
                "student": student
            }
        )

        if not created:
            # Agar allaqachon bor bo‘lsa, student bilan bog‘lash
            bot_user.student = student
            bot_user.username = update.effective_user.username
            bot_user.tg_name = update.effective_user.full_name
            bot_user.save()

        await update.message.reply_text(f"Salom {student.full_name}! Siz ro‘yxatdan o‘tdingiz.")

        return ConversationHandler.END


if __name__ == "__main__":
    bot = Bot()
    bot.run()
