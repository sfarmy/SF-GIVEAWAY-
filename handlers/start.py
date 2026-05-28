from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
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
    save_claim_history
)

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


GROUP = {

    "name": "SF TOOL GC",
    "link": "https://t.me/sf_reset",
    "id": -1002708620916
}


# ================= USER STATE =================
user_state = {}


# ================= FORCE JOIN =================
async def check_force_join(user_id, bot):

    not_joined = []

    # CHANNELS
    for c in CHANNELS:

        try:

            member = await bot.get_chat_member(
                c["id"],
                user_id
            )

            if member.status in ["left", "kicked"]:

                not_joined.append(c)

        except:

            not_joined.append(c)

    # GROUP
    try:

        member = await bot.get_chat_member(
            GROUP["id"],
            user_id
        )

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
🎟️ WELCOME PANEL

🎫 YOUR TICKETS: {tickets}
        """,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # NO RESPONSE IN GROUP / CHANNEL
    if update.effective_chat.type != "private":
        return

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    await add_user(user.id, username)

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
🎉 NEW REFERRAL JOINED

👤 USER: {username}

➕ YOU GOT 10 TICKETS
                            """
                        )

                    except:
                        pass

        except:
            pass

    # ================= START ANIMATION =================
    msg = await update.message.reply_text(
        f"👋 HELLO {username}"
    )

    await asyncio.sleep(1)

    await msg.edit_text(
        "⚡ LOADING..."
    )

    await asyncio.sleep(1)

    # ================= ALWAYS SHOW JOIN PANEL =================
    all_channels = CHANNELS + [GROUP]

    await msg.edit_text(
        """
⚠️ JOIN ALL CHANNELS & GROUP

THEN CLICK VERIFY BUTTON
        """,
        reply_markup=get_join_buttons(all_channels)
    )


# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query

    user_id = q.from_user.id

    await q.answer()

    data = q.data


    # ================= VERIFY JOIN =================
    if data == "check_join":

        not_joined = await check_force_join(
            user_id,
            context.bot
        )

        # NOT JOINED
        if not_joined:

            await q.message.edit_text(
                """
❌ YOU STILL HAVE NOT JOINED ALL CHANNELS

JOIN REMAINING CHANNELS BELOW
                """,
                reply_markup=get_join_buttons(not_joined)
            )

            return

        # VERIFIED
        bonus = await give_welcome_bonus(user_id)

        if bonus == "success":

            await q.message.edit_text(
                """
✅ VERIFIED SUCCESSFULLY

🎁 YOU GOT 15 TICKETS
                """
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

        bot_username = context.bot.username

        ref_link = (
            f"https://t.me/{bot_username}?start={user_id}"
        )

        text = f"""
👤 USER INFO

🆔 ID: {user_id}

🎟️ TICKETS: {tickets}

🔗 REFERRAL LINK:
{ref_link}

🎁 REFER FRIENDS & EARN 10 TICKETS
        """

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


    # ================= LEADERBOARD =================
    if data == "leaderboard":

        users = await top_users()

        text = "🏆 TOP USERS\n\n"

        i = 1

        for u in users:

            name = (
                u[0]
                if u[0]
                else "Unknown"
            )

            text += (
                f"{i}. {name} ➜ {u[1]} tickets\n"
            )

            i += 1

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
            else "⚠️ DAILY BONUS ALREADY CLAIMED"
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
🎁 SEND YOUR REDEEM CODE

Example:
FREE100
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

    # NO RESPONSE IN GROUP
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

        already = await already_claimed_code(
            user_id,
            text
        )

        if already:

            await update.message.reply_text(
                "❌ YOU ALREADY USED THIS CODE"
            )

            user_state[user_id] = None

            return

        result = await use_redeem_code(
            user_id,
            username,
            text
        )

        if result == "invalid":

            await update.message.reply_text(
                "❌ INVALID CODE"
            )

        elif result == "expired":

            await update.message.reply_text(
                "⚠️ CODE EXPIRED"
            )

        elif result == "used":

            await update.message.reply_text(
                "❌ YOU ALREADY USED THIS CODE"
            )

        else:

            await save_claim_history(
                user_id,
                username,
                text
            )

            await update.message.reply_text(
                f"🎉 {result} TICKETS ADDED"
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