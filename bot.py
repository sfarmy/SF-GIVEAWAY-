import asyncio
from telegram.ext import ApplicationBuilder
from config import TOKEN
from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from database.db import init_db

# ================= EVENT LOOP =================
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.run_until_complete(init_db())

# ================= APP =================
app = ApplicationBuilder().token(TOKEN).build()

# ================= ADMIN HANDLERS (FIRST SAFE ROUTE) =================
for handler in get_admin_handlers():
    app.add_handler(handler)

# ================= USER HANDLERS =================
for handler in get_handlers():
    app.add_handler(handler)

print("BOT RUNNING...")

app.run_polling()