from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database.db import (
    add_user,
    get_tickets,
    top_users,
    add_referral,
    claim_daily_bonus,
    give_welcome_bonus,
    use_redeem_code,
    already_claimed_code,
    save_claim_history,
    get_all_users,
    get_total_tickets,
    get_user_rank
)

from handlers.reward import rewards_menu

import asyncio


# ================= CHANNELS =================
CHANNELS = [
    {
        "name": "SF ARMY",
        "link": "https://t.me/+TwoCQG8QZPM1OGRl",
        "id": -1003689156772
    },
    {
        "name": "SF TOOL",
        "link": "https://t.me/anushar_file",
        "id": -1003746793908
    },
    {
        "name": "SF MM",
        "link": "https://t.me/EagleMiddleUpdates",
        "id": -1003971360634
    },
    {
        "name": "SF VOUCHER",
        "link": "https://t.me/eaglevoucher",
        "id": -1003770492772
    },
    {
        "name": "SF GIVEAWAY",
        "link": "https://t.me/sfgiveaways",
        "id": -1003664665551
    }
]

# ================= GROUPS (FIX ADDED ONLY HERE) =================
GROUP = {
    "name": "SF TOOL GC",
    "link": "https://t.me/sf_reset",
    "id": -1002708620916
}

ANOTHER_GROUP = {
    "name": "ANNI SERA GC",
    "link": "https://t.me/annisera",
    "id": -1002759753827
}

user_state = {}

# ================= ADMINS =================
ADMIN_IDS = [7305665779, 7331380618]


# ================= FORCE JOIN (FIXED ONLY) =================
async def check_force_join(user_id, bot):

    not_joined = []

    # channels check
    for c in CHANNELS:
        try:
            member = await bot.get_chat_member(c["id"], user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(c)
        except:
            not_joined.append(c)

    # group 1
    try:
        member = await bot.get_chat_member(GROUP["id"], user_id)
        if member.status in ["left", "kicked"]:
            not_joined.append(GROUP)
    except:
        not_joined.append(GROUP)

    # group 2 (ANNI SERA FIX ADDED)
    try:
        member = await bot.get_chat_member(ANOTHER_GROUP["id"], user_id)
        if member.status in ["left", "kicked"]:
            not_joined.append(ANOTHER_GROUP)
    except:
        not_joined.append(ANOTHER_GROUP)

    return not_joined


# ================= JOIN BUTTONS =================
def get_join_buttons(channels):

    buttons = []

    for c in channels:
        buttons.append([
            InlineKeyboardButton(
                f"📢 {c['name']}",
                url=c["link"]
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "✅ VERIFY JOIN",
            callback_data="check_join"
        )
    ])

    return InlineKeyboardMarkup(buttons)


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
            InlineKeyboardButton("🎟 DAILY BONUS", callback_data="bonus")
        ],

        [
            InlineKeyboardButton("🎁 REWARDS", callback_data="rewards_menu")
        ]
    ]

    await message.edit_text(
        f"""
🎟️ WELCOME SF GIVEAWAY PANEL

🎫 YOUR TICKETS: {tickets}
        """,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= START (ONLY LOADING FIX) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    await add_user(user.id, username)

    # animation (UNCHANGED)
    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1)

    await msg.edit_text("⚡ LOADING PANEL .")
    await asyncio.sleep(0.5)

    await msg.edit_text("⚡ LOADING PANEL ..")
    await asyncio.sleep(0.5)

    await msg.edit_text("⚡ LOADING PANEL ...")
    await asyncio.sleep(1)

    # 🔥 FIX ONLY HERE (was GROUP error + stop issue)
    await msg.edit_text(
        """
⚠️ JOIN ALL CHANNELS & GROUPS

THEN CLICK VERIFY
        """,
        reply_markup=get_join_buttons(CHANNELS + [GROUP, ANOTHER_GROUP])
    )


# ================= CALLBACKS (UNCHANGED) =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user_id = q.from_user.id

    await q.answer()

    data = q.data

    if data == "check_join":

        not_joined = await check_force_join(user_id, context.bot)

        if not_joined:
            await q.message.edit_text(
                "❌ FIRST JOIN ALL CHANNELS",
                reply_markup=get_join_buttons(not_joined)
            )
            return

        bonus = await give_welcome_bonus(user_id)

        if bonus == "success":
            await q.message.edit_text("🎁 +15 WELCOME BONUS ADDED")
            await asyncio.sleep(1)

        await open_main_menu(q.message, user_id)
        return


# ================= HANDLERS =================
def get_handlers():

    return [
        CommandHandler("start", start),
        CallbackQueryHandler(buttons)
    ]