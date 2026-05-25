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


# ================= CHANNELS =================
CHANNELS = [
    {"name": "SF ARMY", "link": "https://t.me/+TwoCQG8QZPM1OGRl", "id": -1003689156772},
    {"name": "SF TOOL", "link": "https://t.me/anushar_file", "id": -1003746793908},
    {"name": "SF MM", "link": "https://t.me/EagleMiddleUpdates", "id": -1003971360634},
    {"name": "SF VOUCHER", "link": "https://t.me/eaglevoucher", "id": -1003770492772},
    {"name": "SF GIVEAWAY", "link": "https://t.me/sfgiveaways", "id": -1003664665551}
]

GROUP = {
    "name": "SF TOOL GC",
    "link": "https://t.me/sf_reset",
    "id": -1002708620916
}


# ================= FORCE JOIN =================
async def check_force_join(user_id, bot):
    try:
        for c in CHANNELS:
            m = await bot.get_chat_member(c["id"], user_id)
            if m.status in ["left", "kicked"]:
                return False

        m = await bot.get_chat_member(GROUP["id"], user_id)
        if m.status in ["left", "kicked"]:
            return False

        return True

    except:
        return False


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

    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1)
    await msg.edit_text("⚡ LOADING...")
    await asyncio.sleep(1)

    buttons = []

    for c in CHANNELS:
        buttons.append([InlineKeyboardButton(f"📢 {c['name']}", url=c["link"])])

    buttons.append([InlineKeyboardButton(f"💬 {GROUP['name']}", url=GROUP["link"])])
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


    # ================= BACK =================
    if data == "back":
        await open_main_menu(q.message, user_id)
        return


    # ================= JOIN CHECK =================
    if data == "check_join":

        if not await check_force_join(user_id, context.bot):
            await q.message.edit_text("❌ JOIN ALL CHANNELS FIRST")
            return

        await q.message.edit_text("✅ VERIFIED")

        ref = context.user_data.get("referrer_id")

        if ref and ref != user_id:

            res = await add_referral(ref, user_id, q.from_user.first_name)

            if res == "success":

                try:
                    await context.bot.send_message(
                        ref,
                        f"🎉 NEW REFERRAL: {q.from_user.first_name}\n🎟 +10 TICKETS"
                    )
                except:
                    pass

                try:
                    await context.bot.send_message(
                        user_id,
                        "🎉 YOU GOT +5 TICKETS"
                    )
                except:
                    pass

            elif res == "already":
                await context.bot.send_message(
                    user_id,
                    "⚠ ALREADY USED REFERRAL"
                )

        await open_main_menu(q.message, user_id)
        return


    # ================= MY INFO =================
    if data == "myinfo":

        tickets = await get_tickets(user_id)

        link = f"https://t.me/{context.bot.username}?start={user_id}"

        await q.message.edit_text(
            f"👤 {q.from_user.first_name}\n🎟 {tickets}\n🔗 {link}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return


    # ================= LEADERBOARD =================
    if data == "leaderboard":

        users = await top_users()

        text = "🏆 TOP USERS\n\n"
        i = 1

        for u in users:
            text += f"{i}. {u[0]} ➜ {u[1]}\n"
            i += 1

        await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return


    # ================= BONUS =================
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


    # ================= REDEEM =================
    if data == "redeem":

        await q.message.edit_text(
            "🎁 REDEEM COMING SOON",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return


    # ================= REWARD =================
    if data == "reward":

        await q.message.edit_text(
            "🏆 REWARD COMING SOON",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return


# ================= HANDLERS =================
def get_handlers():
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(buttons)
    ]