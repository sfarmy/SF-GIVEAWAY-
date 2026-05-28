import asyncio

from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from handlers.reward import get_reward_handlers

from database.db import init_db

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.run_until_complete(init_db())

app = ApplicationBuilder().token(TOKEN).build()

for handler in get_admin_handlers():
    app.add_handler(handler)

for handler in get_handlers():
    app.add_handler(handler)

for handler in get_reward_handlers():
    app.add_handler(handler)


print("BOT RUNNING...")
app.run_polling()