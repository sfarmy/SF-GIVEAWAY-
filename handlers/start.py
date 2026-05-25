from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database.db import *
import asyncio
import aiosqlite


CHANNELS = [
    {"name": "SF ARMY", "link": "https://t.me/+TwoCQG8QZPM1OGRl", "id": -1003689156772}
]

GROUP = {
    "name": "SF TOOL GC",
    "link": "https://t.me/sf_reset",
    "id": -1002708620916
}


async def check_force_join(user_id, bot):
    try:
        for c in CHANNELS:
            m = await bot.get_chat_member(c["id"], user_id)
            if m.status in ["left", "kicked"]:
                return False
        return True
    except:
        return False


async def open_main_menu(message, user_id):

    tickets = await get_tickets(user_id)

    buttons = [
        [
            InlineKeyboardButton("👤 MY INFO", callback_data="myinfo"),
            InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("🎁 REDEEM", callback_data="redeem"),
            InlineKeyboardButton("🎉 REWARD", callback_data="reward")
        ],
        [
            InlineKeyboardButton("🎟 BONUS", callback_data="bonus")
        ]
    ]

    await message.edit_text(
        f"🎟 PANEL\n\n🎫 {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    username = user.first_name

    await add_user(user.id, username)

    await give_welcome_bonus(user.id)

    msg = await update.message.reply_text("👋 STARTING...")

    await asyncio.sleep(1)

    buttons = [
        [InlineKeyboardButton("JOIN CHANNEL", url=CHANNELS[0]["link"])],
        [InlineKeyboardButton("DONE", callback_data="check_join")]
    ]

    await msg.edit_text("JOIN FIRST", reply_markup=InlineKeyboardMarkup(buttons))

    context.user_data["ref"] = context.args[0] if context.args else None


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    uid = q.from_user.id
    await q.answer()

    # JOIN CHECK
    if q.data == "check_join":

        ref = context.user_data.get("ref")

        if ref:
            await add_referral(int(ref), uid, q.from_user.first_name)

        await q.message.edit_text("DONE")
        await open_main_menu(q.message, uid)


    elif q.data == "redeem":
        async with aiosqlite.connect("database.db") as db:
            c = await db.execute("SELECT code FROM redeem_codes WHERE uses_left>0 LIMIT 1")
            data = await c.fetchone()

        if not data:
            await q.message.edit_text("NO REDEEM ACTIVE")
            return

        await q.message.edit_text("ENTER CODE")


    elif q.data == "reward":
        await q.message.edit_text("COMING SOON")


    elif q.data == "back":
        await open_main_menu(q.message, uid)


def get_handlers():
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(buttons)
    ]