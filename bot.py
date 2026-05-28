import asyncio
import os
from datetime import time as dtime

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
            await context.bot.send_message(chat_id=admin, text=text)
        except:
            pass


# ================= DB INIT =================
async def setup_db():
    await init_db()


# ================= MAIN =================
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # handlers
    for h in get_admin_handlers():
        app.add_handler(h)

    for h in get_handlers():
        app.add_handler(h)

    for h in get_reward_handlers():
        app.add_handler(h)

    # job queue
    app.job_queue.run_daily(
        daily_report,
        time=dtime(hour=18, minute=30)  # 12 AM IST
    )

    print("🤖 BOT RUNNING...")

    # 🚨 IMPORTANT: NO asyncio.run()
    app.run_polling(drop_pending_updates=True)


# ================= ENTRY =================
if __name__ == "__main__":

    asyncio.run(setup_db())

    print("✅ DB READY" if os.path.exists(DB_NAME) else "⚠️ DB AUTO CREATE MODE")

    main()