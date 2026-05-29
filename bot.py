import asyncio
import os

from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from handlers.reward import get_reward_handlers

from database.db import init_db, DB_NAME

async def setup_db():
    await init_db()

async def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # START.PY FIRST
    for h in get_handlers():
        app.add_handler(h)

    # REWARD.PY SECOND
    for h in get_reward_handlers():
        app.add_handler(h)

    # ADMIN.PY LAST
    for h in get_admin_handlers():
        app.add_handler(h)

    print("🤖 BOT RUNNING...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(
        drop_pending_updates=True
    )

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":

    asyncio.run(setup_db())

    if os.path.exists(DB_NAME):
        print("✅ DB READY")
    else:
        print("⚠️ DB AUTO CREATE MODE")

    asyncio.run(main())