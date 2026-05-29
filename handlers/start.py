#START.PY (FULL UPDATED CODE)

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

# ================= GROUPS =================
GROUPS = [

    {
        "name": "SF TOOL GC",
        "link": "https://t.me/sf_reset",
        "id": -1002708620916
    },

    {
        "name": "ANNI SERA GC",
        "link": "https://t.me/annisera",
        "id": -1002759753827
    }
]

user_state = {}

# ================= ADMINS =================
ADMIN_IDS = [7305665779, 7331380618]


# ================= FORCE JOIN =================
async def check_force_join(user_id, bot):

    not_joined = []

    for c in CHANNELS:
        try:
            member = await bot.get_chat_member(c["id"], user_id)

            if member.status in ["left", "kicked"]:
                not_joined.append(c)

        except:
            not_joined.append(c)

    try:
        member = await bot.get_chat_member(GROUP["id"], user_id)

        if member.status in ["left", "kicked"]:
            not_joined.append(GROUP)

    except:
        not_joined.append(GROUP)

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
            InlineKeyboardButton(
                "👤 MY INFO",
                callback_data="myinfo"
            ),

            InlineKeyboardButton(
                "🏆 LEADERBOARD",
                callback_data="leaderboard"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 REDEEM CODE",
                callback_data="redeem"
            ),

            InlineKeyboardButton(
                "🎟 DAILY BONUS",
                callback_data="bonus"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 REWARDS",
                callback_data="rewards_menu"
            )
        ]
    ]

    await message.edit_text(
        f"""
🎟️ WELCOME SF GIVEAWAY PANEL

🎫 YOUR TICKETS: {tickets}
        """,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= START =================
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

    # ================= ADMIN NOTIFY =================
    for admin in ADMIN_IDS:

        try:

            await context.bot.send_message(
                admin,
                f"""
🚀 NEW USER STARTED BOT

👤 NAME:
{user.first_name}

🔗 USERNAME:
{username}

🆔 ID:
{user.id}
                """
            )

        except:
            pass

    # ================= REFERRAL =================
    if context.args:

        try:
            referrer_id = int(context.args[0])

            if referrer_id != user.id:

                result = await add_referral(
                    referrer_id,
                    user.id
                )

                if result == "success":

                    try:
                        await context.bot.send_message(
                            referrer_id,
                            f"""
🎉 NEW REFERRAL

👤 {username}
➕ +10 TICKETS
                            """
                        )
                    except:
                        pass

        except:
            pass

    # ================= ANIMATION =================
    msg = await update.message.reply_text(
        f"👋 HELLO {username}"
    )

    await asyncio.sleep(1)

    await msg.edit_text("⚡ LOADING PANEL .")
    await asyncio.sleep(0.5)

    await msg.edit_text("⚡ LOADING PANEL ..")
    await asyncio.sleep(0.5)

    await msg.edit_text("⚡ LOADING PANEL ...")
    await asyncio.sleep(1)

    # ================= FORCE JOIN =================
    await msg.edit_text(
        """
⚠️ JOIN ALL CHANNELS & GROUP

THEN CLICK VERIFY
        """,
        reply_markup=get_join_buttons(
            CHANNELS + [GROUP]
        )
    )


# ================= CALLBACKS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user_id = q.from_user.id

    await q.answer()

    data = q.data


    # ================= VERIFY =================
    if data == "check_join":

        not_joined = await check_force_join(
            user_id,
            context.bot
        )

        if not_joined:

            await q.message.edit_text(
                """
❌ FIRST JOIN ALL CHANNELS
                """,
                reply_markup=get_join_buttons(
                    not_joined
                )
            )

            return

        bonus = await give_welcome_bonus(user_id)

        if bonus == "success":

            await q.message.edit_text(
                "🎁 +15 WELCOME BONUS ADDED"
            )

            await asyncio.sleep(1)

        await open_main_menu(
            q.message,
            user_id
        )

        return


    # ================= MY INFO =================
    if data == "myinfo":

        tickets = await get_tickets(user_id)

        rank = await get_user_rank(user_id)

        ref_link = (
            f"https://t.me/"
            f"{context.bot.username}"
            f"?start={user_id}"
        )

        text = f"""
👤 USER INFO

🆔 USER ID:
{user_id}

🎟 TICKETS:
{tickets}

📊 RANK:
#{rank}

🔗 REFERRAL LINK:
{ref_link}
        """

        await q.message.edit_text(
            text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 BACK",
                        callback_data="back"
                    )
                ]
            ])
        )

        return


    # ================= LEADERBOARD =================
    if data == "leaderboard":

        users = await top_users()

        total_users = len(
            await get_all_users()
        )

        total_tickets = await get_total_tickets()

        rank = await get_user_rank(user_id)

        text = f"""
🏆 LEADERBOARD

👥 USERS:
{total_users}

🎟 TOTAL TICKETS:
{total_tickets}

📊 YOUR RANK:
#{rank}

━━━━━━━━━━━━━━

🔥 TOP 15 USERS

        """

        for i, u in enumerate(users, 1):

            name = u[0] or "Unknown"

            text += (
                f"{i}. {name}"
                f" ➜ {u[1]} tickets\n"
            )

        await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 BACK",
                        callback_data="back"
                    )
                ]
            ])
        )

        return


    # ================= DAILY BONUS =================
    if data == "bonus":

        r = await claim_daily_bonus(user_id)

        txt = (
            "🎉 +2 TICKETS ADDED"
            if r == "success"
            else "⚠️ BONUS ALREADY CLAIMED"
        )

        await q.message.edit_text(
            txt,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 BACK",
                        callback_data="back"
                    )
                ]
            ])
        )

        return


    # ================= REDEEM =================
    if data == "redeem":

        user_state[user_id] = "redeem"

        await q.message.edit_text(
            """
🎁 SEND REDEEM CODE
            """,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 BACK",
                        callback_data="back"
                    )
                ]
            ])
        )

        return


    # ================= BACK =================
    if data == "back":

        await open_main_menu(
            q.message,
            user_id
        )

        return


# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    if not update.message:
        return

    user_id = update.effective_user.id

    text = update.message.text.strip()

    # ================= REDEEM =================
    if user_state.get(user_id) == "redeem":

        username = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else update.effective_user.first_name
        )

        if await already_claimed_code(user_id, text):

            await update.message.reply_text(
                "❌ CODE ALREADY USED"
            )

            user_state[user_id] = None
            return

        result = await use_redeem_code(
            user_id,
            username,
            text
        )

        if result in ["invalid", "expired", "used"]:

            await update.message.reply_text(
                f"❌ {result.upper()}"
            )

        else:

            await save_claim_history(
                user_id,
                username,
                text
            )

            await update.message.reply_text(
                f"🎉 +{result} TICKETS ADDED"
            )

        user_state[user_id] = None


# ================= HANDLERS =================
def get_handlers():

    return [

        CommandHandler(
            "start",
            start
        ),

        CallbackQueryHandler(
            buttons,
            pattern="^(check_join|myinfo|leaderboard|bonus|redeem|back)$"
        ),

        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    ]