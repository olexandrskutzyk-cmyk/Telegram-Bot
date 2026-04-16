from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

import os
TOKEN = os.getenv("TOKEN")

MANAGER_ID = 8046431887
ADMIN_ID = 6014835289

EMPLOYEES = {
    "Женя Варшава": 331538942,
    "Sandra": 6974395486,
}

ID_TO_NAME = {v: k for k, v in EMPLOYEES.items()}

manager_state = {}

# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id == MANAGER_ID:
        keyboard = [[name] for name in EMPLOYEES.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text("👩‍💼 Выбери сотрудника:", reply_markup=reply_markup)

    elif user_id == ADMIN_ID:
        await update.message.reply_text("👀 Режим администратора активен")

    else:
        await update.message.reply_text("Ты подключён")

# обработка сообщений
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # МЕНЕДЖЕР
    if user_id == MANAGER_ID:

        # выбор сотрудника
        if text in EMPLOYEES:
            manager_state[user_id] = text

            keyboard = [["🔁 Сменить сотрудника"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(
                f"💬 Чат с {text} открыт\n\nПиши сообщение:",
                reply_markup=reply_markup
            )

        # смена сотрудника
        elif text == "🔁 Сменить сотрудника":
            keyboard = [[name] for name in EMPLOYEES.keys()]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            manager_state.pop(user_id, None)

            await update.message.reply_text(
                "👩‍💼 Выбери сотрудника:",
                reply_markup=reply_markup
            )

        # отправка сообщения
        else:
            if user_id in manager_state:
                name = manager_state[user_id]
                chat_id = EMPLOYEES[name]

                # сотруднику
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📩 Новое сообщение:\n{text}"
                )

                # админу
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"📤 Менеджер → {name}\n{text}"
                )

            else:
                await update.message.reply_text("❗ Сначала выбери сотрудника")

    # СОТРУДНИК
    elif user_id in ID_TO_NAME:
        name = ID_TO_NAME[user_id]

        # менеджеру
        await context.bot.send_message(
            chat_id=MANAGER_ID,
            text=f"👤 {name}:\n{text}"
        )

        # админу
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 {name} → Менеджер\n{text}"
        )

    else:
        await update.message.reply_text("⛔ Нет доступа")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
