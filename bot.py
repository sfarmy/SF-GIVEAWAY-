import asyncio
from telegram.ext import ApplicationBuilder
from config import TOKEN
from handlers.start import get_handlers
from handlers.admin import get_admin_handlers   # ✅ ADD THIS
from database.db import init_db

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.run_until_complete(init_db())

app = ApplicationBuilder().token(TOKEN).build()

# USER HANDLERS
for h in get_handlers():
    app.add_handler(h)

# ADMIN HANDLERS ✅ (THIS WAS MISSING)
for h in get_admin_handlers():
    app.add_handler(h)

print("BOT RUNNING...")

app.run_polling()