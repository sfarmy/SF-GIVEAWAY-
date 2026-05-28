import asyncio
import os

# ⭐ IMPORTANT FIX (EVENT LOOP ISSUE SOLVE)
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

from telegram.ext import ApplicationBuilder

from config import TOKEN
from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from handlers.reward import get_reward_handlers
from database.db import init_db, DB_NAME


# ================= DB INIT =================
async def setup_db():
    await init_db()


# ================= MAIN BOT =================
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # handlers register
    for h in get_admin_handlers():
        app.add_handler(h)

    for h in get_handlers():
        app.add_handler(h)

    for h in get_reward_handlers():
        app.add_handler(h)

    print("🤖 BOT RUNNING...")

    # start bot
    app.run_polling(drop_pending_updates=True)


# ================= ENTRY =================
if __name__ == "__main__":

    # init database first
    asyncio.run(setup_db())

    # db check
    if os.path.exists(DB_NAME):
        print("✅ DB READY")
    else:
        print("⚠️ DB AUTO CREATE MODE")

    # start bot
    main()