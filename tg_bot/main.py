import os
from datetime import datetime

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

from data.file.generate import generate_contract
from data.student.models import Student
from data.bot.models import BotUser
from data.payment.models import InstallmentPayment, Payment
from data.contract.models import Contract

ASK_JSHSHIR = 1


class Bot:
    def __init__(self):
        BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.app = ApplicationBuilder().token(BOT_TOKEN).post_init(self.post_init).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                ASK_JSHSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_jshshir)]
            },
            fallbacks=[]
        )

        self.app.add_handler(conv_handler)
        self.app.add_handler(MessageHandler(filters.TEXT, self.message_handler))

    async def post_init(self, app):
        await app.bot.set_my_commands([
            BotCommand("start", "Botni ishga tushurish"),
        ])

    def run(self):
        self.app.run_polling()


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Passport JSHSHIR raqamingizni kiriting:"
        )
        return ASK_JSHSHIR

    async def ask_jshshir(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # jshshir = update.message.text.strip()
        jshshir = update.message.text.replace(" ", "").strip()

        try:
            student = Student.objects.get(jshshir=jshshir)
            context.user_data["jshshir"] = jshshir
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
            bot_user.student = student
            bot_user.username = update.effective_user.username
            bot_user.tg_name = update.effective_user.full_name
            bot_user.save()

        # Studentni session/context ga saqlaymiz
        context.user_data["student_id"] = student.id

        buttons = [
            [KeyboardButton("To'lovlar ro'yxatini ko'rish")],
            [KeyboardButton("To'lov shartnomasi olish")],
        ]

        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        text = f"Salom {student.full_name}!\nPastdagi tugmalardan birini tanlang."

        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
        )

        return ConversationHandler.END

    async def message_handler(self, update, context):
        text = update.message.text
        if text == "To'lovlar ro'yxatini ko'rish":
            await self.payments(update, context)

        elif text == "To'lov shartnomasi olish":
            await self.contract_download(update, context)

    async def payments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        student = Student.objects.get(jshshir=context.user_data.get("jshshir"))

        # Contract ma’lumotlari
        contract = Contract.objects.filter(student=student).first()
        contract_sum = contract.period_amount_dt if contract else 0
        contract_sum = f"{contract_sum:,.0f}".replace(",", " ")

        # Fakultet va yo‘nalish (agar mavjud bo‘lsa)
        specialization = getattr(student, "specialization", None)
        faculty_name = specialization.faculty.name if specialization else "Noma’lum"
        specialization_name = specialization.name if specialization else "Noma’lum"

        # To‘langan to‘lovlar
        payments = Payment.objects.filter(student=student).order_by("payment_date")
        payments_text = ""

        if payments.exists():
            payments_text += "✅ To‘langanlar:\n"
            for idx, pay in enumerate(payments, start=1):
                payment_date = pay.payment_date.strftime("%d-%m-%Y")  # sana formatlash
                amount = f"{pay.amount:,.0f}".replace(",", " ")  # sonlarni bo‘sh joy bilan ajratish
                payments_text += f"{idx}) {amount} so‘m — {payment_date}\n"
        else:
            payments_text += "❌ Hali to‘lov qilinmagan.\n"

        # Qolgan qarzlar (InstallmentPayment)
        installment = InstallmentPayment.objects.filter(student=student).first()
        if installment and installment.installment_payments:
            payments_text += "\n📌 Qolgan to‘lovlar jadvali:\n"
            for idx, pay in enumerate(installment.installment_payments, start=1):
                payment_date = datetime.strptime(
                    pay.get("payment_date"), "%Y-%m-%d"
                ).strftime("%d-%m-%Y")  # jsondagi sanani formatlash
                left = f"{int(pay.get('left')):,.0f}".replace(",", " ")  # sonlarni formatlash
                payments_text += f"{idx}) {left} so‘m — {payment_date}\n"

            left_total = f"{installment.left:,.0f}".replace(",", " ")
            payments_text += f"\n💰 Umumiy qolgan to'lov: {left_total} so‘m"
        else:
            payments_text += "\n✅ Qarzdorlik yo‘q."

        # Yakuniy text
        text = (
            f"👤 Talaba: {student.full_name}\n"
            f"🏫 Fakultet: {faculty_name}\n"
            f"📚 Yo‘nalish: {specialization_name}\n"
            f"💳 Kontrakt summasi: {contract_sum} so‘m\n\n"
            f"{payments_text}"
        )

        await update.message.reply_text(text)

    async def contract_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        student = Student.objects.get(jshshir=context.user_data.get("jshshir"))
        print(student)
        student_id = student.id
        print(student_id)

        student = Student.objects.get(pk=student_id)
        contract_file = generate_contract(student)

        await update.message.reply_document(open(contract_file.file.path, "rb"))


if __name__ == "__main__":
    bot = Bot()
    bot.run()
