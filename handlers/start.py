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

import asyncio


# ================= CHANNELS =================
CHANNELS = [
    {"name": "SF ARMY", "link": "https://t.me/+TwoCQG8QZPM1OGRl", "id": -1003689156772},
    {"name": "SF TOOL", "link": "https://t.me/anushar_file", "id": -1003746793908},
    {"name": "SF MM", "link": "https://t.me/EagleMiddleUpdates", "id": -1003971360634},
    {"name": "SF VOUCHER", "link": "https://t.me/eaglevoucher", "id": -1003770492772},
    {"name": "SF GIVEAWAY", "link": "https://t.me/sfgiveaways", "id": -1003664665551}
]

# ================= GROUPS =================
GROUPS = [
    {"name": "SF TOOL GC", "link": "https://t.me/sf_reset", "id": -1002708620916},
    {"name": "ANNI SERA GC", "link": "https://t.me/annisera", "id": -1002759753827}
]

user_state = {}

ADMIN_IDS = [7305665779, 7331380618]

# 🔥 FIX: START TRACKING STORE (ADDED)
start_counter = {}


# ================= FORCE JOIN =================
async def check_force_join(user_id, bot):

    not_joined = []

    for c in CHANNELS:
        try:
            m = await bot.get_chat_member(c["id"], user_id)
            if m.status in ["left", "kicked"]:
                not_joined.append(c)
        except:
            not_joined.append(c)

    for g in GROUPS:
        try:
            m = await bot.get_chat_member(g["id"], user_id)
            if m.status in ["left", "kicked"]:
                not_joined.append(g)
        except:
            not_joined.append(g)

    return not_joined


def get_join_buttons(items):
    buttons = []

    for c in items:
        buttons.append([
            InlineKeyboardButton(f"📢 {c['name']}", url=c["link"])
        ])

    buttons.append([
        InlineKeyboardButton("✅ VERIFY JOIN", callback_data="check_join")
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
        ]
    ]

    await message.edit_text(
        f"🎟️ WELCOME SF GIVEAWAY PANEL\n\n🎫 YOUR TICKETS: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= START (WITH NOTIFICATION FIX RESTORED) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    await add_user(user.id, username)

    # 🔥 FIX: START COUNT + NOTIFICATION SYSTEM
    start_counter[user.id] = start_counter.get(user.id, 0) + 1

    if start_counter[user.id] >= 5:   # 👉 threshold (change if needed)
        for admin in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin,
                    f"⚠️ USER SPAM START DETECTED\n\n👤 {username}\n🆔 {user.id}\n🔁 START COUNT: {start_counter[user.id]}"
                )
            except:
                pass
        start_counter[user.id] = 0  # reset after alert


    # admin notify (original)
    for admin in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin,
                f"🚀 NEW USER\n\n👤 {user.first_name}\n🔗 {username}\n🆔 {user.id}"
            )
        except:
            pass


    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1)
    await msg.edit_text("⚡ LOADING PANEL .")
    await asyncio.sleep(0.5)
    await msg.edit_text("⚡ LOADING PANEL ..")
    await asyncio.sleep(0.5)
    await msg.edit_text("⚡ LOADING PANEL ...")
    await asyncio.sleep(0.5)

    await msg.edit_text(
        "⚠️ JOIN ALL CHANNELS & GROUP\nTHEN CLICK VERIFY",
        reply_markup=get_join_buttons(CHANNELS + GROUPS)
    )


# ================= CALLBACK =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user_id = q.from_user.id

    await q.answer()

    if q.data == "check_join":

        not_joined = await check_force_join(user_id, context.bot)

        if not_joined:
            await q.message.edit_text(
                "❌ FIRST JOIN ALL CHANNELS",
                reply_markup=get_join_buttons(not_joined)
            )
            return

        await give_welcome_bonus(user_id)
        await open_main_menu(q.message, user_id)
        return

    if q.data == "back":
        await open_main_menu(q.message, user_id)
        return


# ================= HANDLERS =================
def get_handlers():

    return [
        CommandHandler("start", start),

        CallbackQueryHandler(
            buttons,
            pattern="^(check_join|myinfo|leaderboard|bonus|redeem|back)$"
        ),

        MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None)
    ]