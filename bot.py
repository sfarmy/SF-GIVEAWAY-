import asyncio
import os

from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from handlers.reward import get_reward_handlers

from database.db import init_db, migrate_db, DB_NAME


# ================= SETUP DB =================
async def setup_db():
    # 1. create tables if not exist
    await init_db()

    # 2. fix old DB schema (IMPORTANT FIX)
    await migrate_db()


# ================= MAIN =================
async def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # ================= START.PY HANDLERS =================
    for h in get_handlers():
        app.add_handler(h, group=0)

    # ================= REWARD.PY HANDLERS =================
    for h in get_reward_handlers():
        app.add_handler(h, group=1)

    # ================= ADMIN.PY HANDLERS =================
    for h in get_admin_handlers():
        app.add_handler(h, group=2)

    print("🤖 BOT RUNNING...")

    await app.initialize()
    await app.start()

    await app.updater.start_polling(drop_pending_updates=True)

    # keep alive
    while True:
        await asyncio.sleep(3600)


# ================= ENTRY POINT =================
if __name__ == "__main__":

    # DB setup first (CRITICAL)
    asyncio.run(setup_db())

    # DB status check
    if os.path.exists(DB_NAME):
        print("✅ DB READY")
    else:
        print("⚠️ DB AUTO CREATE MODE")

    # start bot
    asyncio.run(main())