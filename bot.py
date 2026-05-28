import asyncio
import os

from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from handlers.reward import get_reward_handlers  # ✅ MUST MATCH FILE NAME EXACTLY

from database.db import init_db, DB_NAME


# ================= INIT DB =================
async def setup_db():
    await init_db()


# ================= MAIN =================
def main():

    # create bot
    app = ApplicationBuilder().token(TOKEN).build()

    # admin handlers
    for handler in get_admin_handlers():
        app.add_handler(handler)

    # start handlers
    for handler in get_handlers():
        app.add_handler(handler)

    # reward handlers
    for handler in get_reward_handlers():
        app.add_handler(handler)

    print("🤖 BOT RUNNING...")

    # run bot
    app.run_polling(drop_pending_updates=True)


# ================= ENTRY =================
if __name__ == "__main__":
    asyncio.run(setup_db())

    if os.path.exists(DB_NAME):
        print("✅ DATABASE CONNECTED")
    else:
        print("❌ DATABASE FILE NOT FOUND (will auto create if init_db works)")

    main()