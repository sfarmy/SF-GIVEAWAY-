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


# ==========================================
# CHANNELS
# ==========================================
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


# ==========================================
# FORCE CHECK
# ==========================================
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

    except Exception as e:
        print(e)
        return False


# ==========================================
# MAIN MENU
# ==========================================
async def open_main_menu(message, user_id):

    tickets = await get_tickets(user_id)

    buttons = [
        [
            InlineKeyboardButton("👤 MY INFO", callback_data="myinfo"),
            InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("🎉 DAILY BONUS", callback_data="bonus"),
            InlineKeyboardButton("🎁 REDEEM CODE", callback_data="redeem")
        ],
        [
            InlineKeyboardButton("🎁 REWARD", callback_data="reward")
        ]
    ]

    await message.edit_text(
        f"🎟️ WELCOME PANEL\n\n🎫 YOUR TICKETS: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================
# START
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    referrer_id = None
    if context.args:
        try:
            referrer_id = int(context.args[0])
        except:
            pass

    await add_user(user.id, username)

    context.user_data["referrer_id"] = referrer_id

    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1)
    await msg.edit_text("⚡ LOADING...")
    await asyncio.sleep(1)

    join_buttons = []

    for c in CHANNELS:
        join_buttons.append([InlineKeyboardButton(c["name"], url=c["link"])])

    join_buttons.append([InlineKeyboardButton(GROUP["name"], url=GROUP["link"])])
    join_buttons.append([InlineKeyboardButton("✅ DONE JOINING", callback_data="check_join")])

    await msg.edit_text(
        "⚠️ JOIN CHANNELS TO CONTINUE",
        reply_markup=InlineKeyboardMarkup(join_buttons)
    )


# ==========================================
# BUTTONS
# ==========================================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # JOIN CHECK
    if query.data == "check_join":

        joined = await check_force_join(user_id, context.bot)

        if not joined:
            await query.message.edit_text("❌ JOIN ALL CHANNELS FIRST")
            return

        await query.message.edit_text("✅ VERIFIED SUCCESS")

        # REFERRAL ONLY AFTER JOIN
        referrer_id = context.user_data.get("referrer_id")

        if referrer_id and referrer_id != user_id:

            result, name = await add_referral(referrer_id, user_id)

            if result == "success":
                await context.bot.send_message(referrer_id, f"🎉 NEW USER: {name}\n+10 TICKETS")
                await context.bot.send_message(user_id, "🎉 +5 TICKETS RECEIVED")

            elif result == "already":
                await context.bot.send_message(user_id, "⚠️ REFERRAL ALREADY USED")

        await open_main_menu(query.message, user_id)


    elif query.data == "myinfo":
        t = await get_tickets(user_id)
        await query.message.edit_text(f"👤 INFO\n🎟️ {t}")


    elif query.data == "leaderboard":
        users = await top_users()
        text = "🏆 TOP USERS\n\n"
        i = 1
        for u in users:
            text += f"{i}. {u[0]} ➜ {u[1]}\n"
            i += 1

        await query.message.edit_text(text)


    elif query.data == "bonus":
        res = await claim_daily_bonus(user_id)

        if res == "success":
            txt = "🎉 +2 TICKETS"
        elif res == "already":
            txt = "⚠️ ALREADY CLAIMED"
        else:
            txt = "❌ ERROR"

        await query.message.edit_text(txt)


    elif query.data == "back":
        await open_main_menu(query.message, user_id)


# ==========================================
# HANDLER
# ==========================================
def get_handlers():
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(buttons)
    ]