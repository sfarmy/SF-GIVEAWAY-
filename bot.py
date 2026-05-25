import asyncio
from telegram.ext import ApplicationBuilder
from config import TOKEN
from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from database.db import init_db

# ================= EVENT LOOP =================
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ================= INIT DB =================
loop.run_until_complete(init_db())

# ================= APP =================
app = ApplicationBuilder().token(TOKEN).build()

# ================= ADMIN HANDLERS (IMPORTANT FIRST) =================
for h in get_admin_handlers():
    app.add_handler(h)

# ================= USER HANDLERS =================
for h in get_handlers():
    app.add_handler(h)

print("BOT RUNNING...")

app.run_polling()