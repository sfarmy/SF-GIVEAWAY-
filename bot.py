from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers

from database.db import init_db


# ==========================================
# DATABASE INIT
# ==========================================

import asyncio

asyncio.run(init_db())


# ==========================================
# BOT
# ==========================================

app = ApplicationBuilder().token(TOKEN).build()


# ==========================================
# HANDLERS
# ==========================================

for handler in get_handlers():

    app.add_handler(handler)


print("BOT RUNNING...")


# ==========================================
# START BOT
# ==========================================

app.run_polling()