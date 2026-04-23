import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database import (
    add_movie, delete_movie, get_all_movies,
    get_movie_count, get_user_count, get_all_user_ids
)
from keyboards import admin_panel_keyboard, cancel_keyboard, main_menu_keyboard

router = Router()


def admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id != ADMIN_ID:
            return
        return await func(message, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ── FSM States ────────────────────────────────────────────

class AddMovieState(StatesGroup):
    waiting_file = State()
    waiting_code = State()
    waiting_title = State()
    waiting_description = State()


class DeleteMovieState(StatesGroup):
    waiting_code = State()


class BroadcastState(StatesGroup):
    waiting_message = State()


# ── /admin command ────────────────────────────────────────

@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    movie_count = await get_movie_count()
    user_count = await get_user_count()
    await message.answer(
        f"👑 <b>Admin Panel</b>\n\n"
        f"🎬 Kinolar soni: <b>{movie_count}</b>\n"
        f"👥 Foydalanuvchilar: <b>{user_count}</b>\n\n"
        f"Quyidagi tugmalardan birini tanlang:",
        reply_markup=admin_panel_keyboard()
    )


# ── Orqaga ────────────────────────────────────────────────

@router.message(F.text == "🔙 Orqaga")
async def back_handler(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await message.answer(
        "🏠 Asosiy menyu:",
        reply_markup=main_menu_keyboard()
    )


# ── Bekor qilish ──────────────────────────────────────────

@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await message.answer("❌ Amal bekor qilindi.", reply_markup=admin_panel_keyboard())


# ══════════════════════════════════════════════════════════
#  ➕ KINO QO'SHISH
# ══════════════════════════════════════════════════════════

@router.message(F.text == "➕ Kino qo'shish")
async def start_add_movie(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(AddMovieState.waiting_file)
    await message.answer(
        "📤 <b>Kino faylini yuboring</b>\n\n"
        "⚠️ Faylni <b>video</b> sifatida yuboring (siqilgan fayl emas):",
        reply_markup=cancel_keyboard()
    )


@router.message(AddMovieState.waiting_file, F.video)
async def receive_movie_file(message: Message, state: FSMContext):
    await state.update_data(file_id=message.video.file_id)
    await state.set_state(AddMovieState.waiting_code)
    await message.answer(
        "✅ Fayl qabul qilindi!\n\n"
        "📌 <b>Kino kodini kiriting</b> (faqat raqam):\n"
        "Masalan: <code>1234</code>"
    )


@router.message(AddMovieState.waiting_file)
async def wrong_file(message: Message):
    if message.text == "❌ Bekor qilish":
        return
    await message.answer("⚠️ Iltimos, faylni <b>video</b> sifatida yuboring!")


@router.message(AddMovieState.waiting_code)
async def receive_movie_code(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_keyboard())
        return
    code = message.text.strip()
    if not code.isdigit():
        await message.answer("⚠️ Kod faqat <b>raqamlardan</b> iborat bo'lishi kerak!")
        return
    await state.update_data(code=code)
    await state.set_state(AddMovieState.waiting_title)
    await message.answer("🎬 <b>Kino nomini</b> kiriting:")


@router.message(AddMovieState.waiting_title)
async def receive_movie_title(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_keyboard())
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddMovieState.waiting_description)
    await message.answer(
        "📝 <b>Tavsif kiriting</b> (ixtiyoriy):\n"
        "O'tkazib yuborish uchun <b>-</b> yuboring"
    )


@router.message(AddMovieState.waiting_description)
async def receive_movie_description(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_keyboard())
        return

    description = "" if message.text.strip() == "-" else message.text.strip()
    data = await state.get_data()
    await state.clear()

    success = await add_movie(
        code=data['code'],
        title=data['title'],
        file_id=data['file_id'],
        description=description
    )

    if success:
        await message.answer(
            f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🎬 Nomi: <b>{data['title']}</b>\n"
            f"📌 Kod: <code>{data['code']}</code>\n"
            f"📝 Tavsif: {description or "yuq"}",
            reply_markup=admin_panel_keyboard()
        )
    else:
        await message.answer(
            f"❌ <b>{data['code']}</b> kodi allaqachon mavjud!\n"
            "Boshqa kod bilan qayta urinib ko'ring.",
            reply_markup=admin_panel_keyboard()
        )


# ══════════════════════════════════════════════════════════
#  🗑 KINO O'CHIRISH
# ══════════════════════════════════════════════════════════

@router.message(F.text == "🗑 Kino o'chirish")
async def start_delete_movie(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    movies = await get_all_movies()
    if not movies:
        await message.answer("📭 Hozircha hech qanday kino yo'q.")
        return

    await state.set_state(DeleteMovieState.waiting_code)
    await message.answer(
        "🗑 <b>O'chirmoqchi bo'lgan kino kodini kiriting:</b>",
        reply_markup=cancel_keyboard()
    )


@router.message(DeleteMovieState.waiting_code)
async def delete_movie_handler(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_keyboard())
        return

    code = message.text.strip()
    success = await delete_movie(code)
    await state.clear()

    if success:
        await message.answer(
            f"✅ <b>{code}</b> kodli kino o'chirildi!",
            reply_markup=admin_panel_keyboard()
        )
    else:
        await message.answer(
            f"❌ <b>{code}</b> kodli kino topilmadi!",
            reply_markup=admin_panel_keyboard()
        )


# ══════════════════════════════════════════════════════════
#  📋 KINO KODLARI
# ══════════════════════════════════════════════════════════

@router.message(F.text == "📋 Kino kodlari")
async def list_movie_codes(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    movies = await get_all_movies()

    if not movies:
        await message.answer("📭 Hozircha hech qanday kino yo'q.")
        return

    text = f"📋 <b>Barcha kinolar ({len(movies)} ta):</b>\n\n"
    for m in movies:
        text += f"📌 <code>{m['code']}</code> — <b>{m['title']}</b>\n"
        if m['description']:
            text += f"   📝 {m['description']}\n"
        text += "\n"

    # Agar xabar juda uzun bo'lsa, bo'lib yuboramiz
    if len(text) > 4000:
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await message.answer(chunk)
    else:
        await message.answer(text)


# ══════════════════════════════════════════════════════════
#  📣 HAMMAGA XABAR
# ══════════════════════════════════════════════════════════

@router.message(F.text == "📣 Hammaga xabar")
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(BroadcastState.waiting_message)
    user_count = await get_user_count()
    await message.answer(
        f"📣 <b>Hammaga xabar yuborish</b>\n\n"
        f"👥 Foydalanuvchilar soni: <b>{user_count}</b>\n\n"
        f"Yuboriladigan xabarni kiriting (matn, rasm yoki video bo'lishi mumkin):",
        reply_markup=cancel_keyboard()
    )


@router.message(BroadcastState.waiting_message)
async def send_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_keyboard())
        return

    await state.clear()
    user_ids = await get_all_user_ids()

    sent = 0
    failed = 0
    status_msg = await message.answer(
        f"⏳ Xabar yuborilmoqda... 0/{len(user_ids)}"
    )

    for i, user_id in enumerate(user_ids):
        try:
            await message.copy_to(user_id)
            sent += 1
        except Exception:
            failed += 1

        # Har 20 ta foydalanuvchidan keyin statusni yangilaymiz
        if (i + 1) % 20 == 0:
            try:
                await status_msg.edit_text(
                    f"⏳ Xabar yuborilmoqda... {i+1}/{len(user_ids)}"
                )
            except Exception:
                pass

        await asyncio.sleep(0.05)  # flood limitdan himoya

    await status_msg.edit_text(
        f"✅ <b>Xabar yuborish yakunlandi!</b>\n\n"
        f"✅ Yuborildi: <b>{sent}</b>\n"
        f"❌ Xato: <b>{failed}</b>"
    )
    await message.answer("📣 Broadcast tugadi.", reply_markup=admin_panel_keyboard())
