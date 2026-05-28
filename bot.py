import asyncio
import os

from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers
from handlers.admin import get_admin_handlers
from handlers.reward import get_reward_handlers

from database.db import init_db, DB_NAME, get_total_users, get_total_tickets


ADMIN_IDS = [7305665779, 7331380618]


# ================= DAILY REPORT =================
async def daily_report(context):

    users = await get_total_users()
    tickets = await get_total_tickets()

    text = f"""
📊 DAILY REPORT (IST)

👥 TOTAL USERS: {users}
🎟 TOTAL TICKETS: {tickets}
"""

    for admin in ADMIN_IDS:
        try:
            await context.bot.send_message(admin, text)
        except:
            pass


# ================= DB INIT =================
async def setup_db():
    await init_db()


# ================= FIX LOOP ISSUE =================
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# ================= MAIN =================
def main():

    # ✔ IMPORTANT FIX: ensure loop exists before builder
    asyncio.set_event_loop(asyncio.get_event_loop())

    app = ApplicationBuilder().token(TOKEN).build()

    # handlers
    for handler in get_admin_handlers():
        app.add_handler(handler)

    for handler in get_handlers():
        app.add_handler(handler)

    for handler in get_reward_handlers():
        app.add_handler(handler)

    # daily job
    app.job_queue.run_daily(
        daily_report,
        time=__import__("datetime").time(hour=18, minute=30)
    )

    print("🤖 BOT RUNNING...")

    app.run_polling(drop_pending_updates=True)


# ================= ENTRY =================
if __name__ == "__main__":

    asyncio.run(setup_db())

    print("✅ DB READY" if os.path.exists(DB_NAME) else "⚠️ DB AUTO CREATE MODE")

    main()