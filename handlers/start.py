from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database.db import (
    add_user,
    get_tickets,
    top_users,
    add_referral,
    claim_daily_bonus,
    give_welcome_bonus
)

import asyncio


CHANNELS = [
    {"name": "SF ARMY", "link": "https://t.me/+TwoCQG8QZPM1OGRl", "id": -1003689156772},
    {"name": "SF TOOL", "link": "https://t.me/anushar_file", "id": -1003746793908},
]

GROUP = {
    "name": "SF TOOL GC",
    "link": "https://t.me/sf_reset",
    "id": -1002708620916
}


# ================= MAIN MENU =================
async def open_main_menu(message, user_id):

    tickets = await get_tickets(user_id)

    buttons = [
        [
            InlineKeyboardButton("👤 MY INFO", callback_data="myinfo"),
            InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("🎁 REDEEM CODE", callback_data="redeem"),
            InlineKeyboardButton("🎉 REWARD", callback_data="reward")
        ],
        [
            InlineKeyboardButton("🎟 DAILY BONUS", callback_data="bonus")
        ]
    ]

    await message.edit_text(
        f"🎟 WELCOME PANEL\n\n🎫 TICKETS: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    await add_user(user.id, username)
    await give_welcome_bonus(user.id)

    msg = await update.message.reply_text("👋 HELLO")
    await asyncio.sleep(1)

    buttons = []
    for c in CHANNELS:
        buttons.append([InlineKeyboardButton(f"📢 {c['name']}", url=c["link"])])

    buttons.append([InlineKeyboardButton("💬 JOIN GROUP", url=GROUP["link"])])
    buttons.append([InlineKeyboardButton("✅ DONE JOINING", callback_data="check_join")])

    await msg.edit_text(
        "⚠ JOIN CHANNELS FIRST",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    context.user_data["referrer_id"] = context.args[0] if context.args else None


# ================= BUTTON HANDLER =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user_id = q.from_user.id
    await q.answer()

    data = q.data

    # ===== BACK FIX (MOST IMPORTANT) =====
    if data == "back":
        await open_main_menu(q.message, user_id)
        return

    # ===== REDEEM =====
    if data == "redeem":
        await q.message.edit_text(
            "🎁 REDEEM SYSTEM",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return

    # ===== REWARD =====
    if data == "reward":
        await q.message.edit_text(
            "🏆 REWARD SYSTEM",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return

    # ===== LEADERBOARD =====
    if data == "leaderboard":
        users = await top_users()
        text = "🏆 TOP USERS\n\n"

        for i, u in enumerate(users, 1):
            text += f"{i}. {u[0]} ➜ {u[1]}\n"

        await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return

    # ===== MY INFO =====
    if data == "myinfo":
        tickets = await get_tickets(user_id)
        await q.message.edit_text(
            f"👤 USER\n🎟 {tickets}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return

    # ===== BONUS =====
    if data == "bonus":
        r = await claim_daily_bonus(user_id)
        txt = "🎉 +2 TICKETS" if r == "success" else "⚠ ALREADY CLAIMED"

        await q.message.edit_text(
            txt,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return


def get_handlers():
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(buttons)
    ]