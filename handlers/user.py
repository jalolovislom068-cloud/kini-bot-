from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from config import CHANNEL_USERNAME, CHANNEL_LINK, ADMIN_ID
from database import add_user, get_movie
from keyboards import subscription_keyboard, main_menu_keyboard

router = Router()


async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in ("left", "kicked", "banned")
    except Exception:
        return False


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    await add_user(user.id, user.username or "", user.full_name or "")

    if user.id == ADMIN_ID:
        from keyboards import admin_panel_keyboard
        await message.answer(
            "👑 <b>Admin, xush kelibsiz!</b>",
            reply_markup=admin_panel_keyboard()
        )
        return

    is_subscribed = await check_subscription(bot, user.id)

    if not is_subscribed:
        await message.answer(
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "🎬 <b>Kino Botga Xush Kelibsiz!</b>\n\n"
            "Botdan foydalanish uchun avval quyidagi kanalga obuna bo'ling:",
            reply_markup=subscription_keyboard(CHANNEL_LINK)
        )
    else:
        await message.answer(
            "🎬 <b>Kino Botga Xush Kelibsiz!</b>\n\n"
            f"Kino kodini yuboring.\n"
            f"Kodlarni olish uchun: {CHANNEL_LINK}",
            reply_markup=main_menu_keyboard()
        )


@router.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    is_subscribed = await check_subscription(bot, callback.from_user.id)

    if is_subscribed:
        await callback.message.delete()
        await callback.message.answer(
            "✅ <b>Obuna tasdiqlandi!</b>\n\n"
            f"🎬 Endi kino kodini yuboring.\n"
            f"Kodlarni olish uchun: {CHANNEL_LINK}",
            reply_markup=main_menu_keyboard()
        )
    else:
        await callback.answer(
            "❌ Siz hali obuna bo'lmadingiz! Iltimos avval obuna bo'ling.",
            show_alert=True
        )


@router.message(F.text == "🎬 Kino qidirish")
async def search_movie_prompt(message: Message):
    await message.answer(
        "🔍 Kino kodini yuboring:\n"
        f"Kodlarni olish uchun: {CHANNEL_LINK}"
    )


@router.message(F.text.regexp(r'^\d+$'))
async def get_movie_handler(message: Message, bot: Bot):
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        return  # admin handleriga o'tadi

    is_subscribed = await check_subscription(bot, user_id)
    if not is_subscribed:
        await message.answer(
            "⚠️ Botdan foydalanish uchun kanalga obuna bo'ling:",
            reply_markup=subscription_keyboard(CHANNEL_LINK)
        )
        return

    code = message.text.strip()
    movie = await get_movie(code)

    if not movie:
        await message.answer(
            f"❌ <b>{code}</b> kodga kino mavjud emas!\n\n"
            "Iltimos to'g'ri kod yuboring.\n"
            f"Kodlarni olish uchun {CHANNEL_LINK} kanaliga obuna bo'ling."
        )
        return

    caption = f"🎬 <b>{movie['title']}</b>\n📌 Kod: <code>{movie['code']}</code>"
    if movie['description']:
        caption += f"\n\n📝 {movie['description']}"

    await message.answer_video(
        video=movie['file_id'],
        caption=caption
    )
