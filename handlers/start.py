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


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    referrer_id = None
    if context.args:
        try:
            referrer_id = int(context.args[0])
        except:
            pass

    # save user
    await add_user(user.id, username)

    # ONE TIME WELCOME BONUS (SAFE)
    await give_welcome_bonus(user.id)

    context.user_data["referrer_id"] = referrer_id

    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1)
    await msg.edit_text("⚡ LOADING...")
    await asyncio.sleep(1)

    buttons = [
        [InlineKeyboardButton(f"📢 {c['name']}", url=c["link"])]
        for c in CHANNELS
    ]

    buttons.append([InlineKeyboardButton(f"💬 {GROUP['name']}", url=GROUP["link"])])
    buttons.append([InlineKeyboardButton("✅ DONE JOINING", callback_data="check_join")])

    await msg.edit_text(
        "⚠️ JOIN ALL CHANNELS & GROUP TO CONTINUE ⚠️",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user_id = q.from_user.id
    await q.answer()

    # -------- JOIN CHECK --------
    if q.data == "check_join":

        if not await check_force_join(user_id, context.bot):
            await q.message.edit_text("❌ JOIN ALL CHANNELS FIRST")
            return

        await q.message.edit_text("✅ VERIFIED SUCCESS")

        # -------- REFERRAL (ONLY AFTER JOIN) --------
        referrer_id = context.user_data.get("referrer_id")

        if referrer_id and referrer_id != user_id:

            result = await add_referral(referrer_id, user_id)

            if result == "success":
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text="🎉 REFERRAL SUCCESS\n🎟️ +10 TICKETS"
                    )
                except:
                    pass

                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="🎉 REFERRAL BONUS RECEIVED\n🎟️ +5 TICKETS"
                    )
                except:
                    pass

            elif result == "already":
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="⚠️ REFERRAL ALREADY USED (ONE TIME ONLY)"
                    )
                except:
                    pass

        await open_menu(q.message, user_id)


    # -------- MY INFO --------
    elif q.data == "myinfo":

        tickets = await get_tickets(user_id)

        username = q.from_user.username
        username = f"@{username}" if username else q.from_user.first_name

        refer_link = f"https://t.me/{context.bot.username}?start={user_id}"

        await q.message.edit_text(
            f"👤 USER: {username}\n🎟️ {tickets}\n\n🔗 {refer_link}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )


    # -------- LEADERBOARD --------
    elif q.data == "leaderboard":

        users = await top_users()

        text = "🏆 TOP USERS\n\n"
        i = 1

        for u in users:
            text += f"{i}. {u[0] or 'Unknown'} ➜ 🎟️ {u[1]}\n"
            i += 1

        await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )


    # -------- DAILY BONUS --------
    elif q.data == "bonus":

        result = await claim_daily_bonus(user_id)

        if result == "success":
            text = "🎉 DAILY BONUS CLAIMED\n🎟️ +2"

        elif result == "already":
            text = "⚠️ ALREADY CLAIMED\n⏳ NEXT RESET 12:00 AM"

        else:
            text = "❌ ERROR"

        await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )


    # -------- BACK --------
    elif q.data == "back":
        await open_menu(q.message, user_id)


# ================= MENU =================
async def open_menu(message, user_id):

    tickets = await get_tickets(user_id)

    buttons = [
        [
            InlineKeyboardButton("👤 MY INFO", callback_data="myinfo"),
            InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("🎉 DAILY BONUS", callback_data="bonus")
        ]
    ]

    await message.edit_text(
        f"🎟️ PANEL\n\nTICKETS: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= HANDLERS =================
def get_handlers():
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(buttons)
    ]