# 🎬 Kino Bot

Aiogram 3 asosida qurilgan professional Telegram kino bot.

## 📁 Fayl tuzilmasi

```
kino_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Token va sozlamalar
├── database.py         # SQLite baza
├── keyboards.py        # Tugmalar
├── requirements.txt    # Kutubxonalar
└── handlers/
    ├── __init__.py
    ├── user.py         # Foydalanuvchi handlerlari
    └── admin.py        # Admin handlerlari
```

## 🚀 Ishga tushirish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. config.py ni sozlash
```python
BOT_TOKEN = "sizning_bot_tokeningiz"  # @BotFather dan oling
ADMIN_ID = 8560459628                  # Telegram ID
CHANNEL_USERNAME = "@uzbmediakino"    # Kanal username
CHANNEL_LINK = "https://t.me/uzbmediakino"
```

### 3. Botni ishga tushirish
```bash
python bot.py
```

## ⚙️ Admin komandalar

| Tugma | Vazifa |
|-------|--------|
| ➕ Kino qo'shish | Yangi kino qo'shish (fayl → kod → nom → tavsif) |
| 🗑 Kino o'chirish | Kodga qarab kino o'chirish |
| 📋 Kino kodlari | Barcha kinolar ro'yxati |
| 📣 Hammaga xabar | Broadcast - barcha foydalanuvchilarga xabar |
| 🔙 Orqaga | Oddiy menyu |

## 👤 Foydalanuvchi

1. `/start` → kanal obuna tekshiriladi
2. Kino kodini yozadi (masalan: `1234`)
3. Bot kinoni yuboradi

## ⚠️ Muhim

- Bot `@uzbmediakino` kanalida **admin** bo'lishi kerak (obuna tekshirish uchun)
- Yoki kanalda bot adminligiga ehtiyoj yo'q, lekin kanal **public** bo'lishi kerak
