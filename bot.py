import asyncio

from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from database.db import init_db


# ================= EVENT LOOP FIX =================
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# ================= INIT DATABASE =================
loop.run_until_complete(init_db())


# ================= BOT APP =================
app = ApplicationBuilder().token(TOKEN).build()


# ================= HANDLERS REGISTER =================

# user handlers
for handler in get_handlers():
    app.add_handler(handler)

# admin handlers
for handler in get_admin_handlers():
    app.add_handler(handler)


print("🤖 BOT RUNNING...")


# ================= START BOT =================
app.run_polling()