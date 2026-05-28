import asyncio
import os

from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from handlers.reward import get_reward_handlers

from database.db import init_db, DB_NAME


# ================= CREATE LOOP =================
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# ================= INIT DATABASE =================
loop.run_until_complete(init_db())


# ================= CHECK DB =================
if not os.path.exists(DB_NAME):

    print("❌ DATABASE FILE NOT FOUND")

else:

    print("✅ DATABASE CONNECTED")


# ================= CREATE BOT =================
app = ApplicationBuilder().token(TOKEN).build()


# ================= ADMIN HANDLERS =================
for handler in get_admin_handlers():

    app.add_handler(handler)


# ================= START HANDLERS =================
for handler in get_handlers():

    app.add_handler(handler)


# ================= REWARD HANDLERS =================
for handler in get_reward_handlers():

    app.add_handler(handler)


# ================= BOT START =================
print("🤖 BOT RUNNING...")


# ================= RUN BOT =================
app.run_polling(
    drop_pending_updates=True
)