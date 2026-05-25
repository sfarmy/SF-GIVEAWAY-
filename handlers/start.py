from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from database.users import (
    add_user,
    get_tickets,
    get_top_users
)

import asyncio


# ==========================================
# CHANNELS LINK + ID
# ==========================================

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


# ==========================================
# GROUP LINK + ID
# ==========================================

GROUP = {
    "name": "SF TOOL GC",
    "link": "https://t.me/sf_reset",
    "id": -1002708620916
}


# ==========================================
# FORCE JOIN CHECK
# ==========================================

async def check_force_join(user_id, bot):

    try:

        for channel in CHANNELS:

            member = await bot.get_chat_member(
                channel["id"],
                user_id
            )

            if member.status in ["left", "kicked"]:
                return False

        member = await bot.get_chat_member(
            GROUP["id"],
            user_id
        )

        if member.status in ["left", "kicked"]:
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
            )
        ],

        [
            InlineKeyboardButton(
                "🎉 BONUS",
                callback_data="bonus"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await message.edit_text(

        f"🎟️ WELCOME TO SF GIVEAWAY PANEL\n\n"
        f"🎫 YOUR TICKETS: {tickets}",

        reply_markup=reply_markup
    )


# ==========================================
# START COMMAND
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    # SAVE USER
    await add_user(
        user.id,
        username
    )

    # HELLO MESSAGE
    msg = await update.message.reply_text(
        f"👋 HELLO {username}"
    )

    await asyncio.sleep(1.5)

    # LOADING EFFECT
    await msg.edit_text("⚡ LOADING...")
    await asyncio.sleep(1)

    await msg.edit_text("🔍 CHECKING SYSTEM...")
    await asyncio.sleep(1)

    await msg.edit_text("📢 PREPARING CHANNELS...")
    await asyncio.sleep(1)

    # JOIN BUTTONS
    join_buttons = []

    for channel in CHANNELS:

        join_buttons.append(
            [
                InlineKeyboardButton(
                    f"📢 {channel['name']}",
                    url=channel["link"]
                )
            ]
        )

    join_buttons.append(
        [
            InlineKeyboardButton(
                f"💬 {GROUP['name']}",
                url=GROUP["link"]
            )
        ]
    )

    join_buttons.append(
        [
            InlineKeyboardButton(
                "✅ DONE JOINING",
                callback_data="check_join"
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(join_buttons)

    await msg.edit_text(
        "⚠️ JOIN ALL CHANNELS & GROUP TO CONTINUE ⚠️",
        reply_markup=reply_markup
    )


# ==========================================
# BUTTON HANDLER
# ==========================================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    # ======================================
    # CHECK JOIN
    # ======================================

    if query.data == "check_join":

        await query.message.edit_text(
            "🔍 CHECKING JOIN STATUS..."
        )

        await asyncio.sleep(1)

        await query.message.edit_text(
            "⚡ VERIFYING CHANNELS..."
        )

        await asyncio.sleep(1)

        joined = await check_force_join(
            user_id,
            context.bot
        )

        # SUCCESS
        if joined:

            await query.message.edit_text(
                "✅ VERIFIED SUCCESSFULLY 🔥\n\n🎉 YOU JOINED ALL CHANNELS & GROUP"
            )

            await asyncio.sleep(2)

            await open_main_menu(
                query.message,
                user_id
            )

        # FAILED
        else:

            join_buttons = []

            for channel in CHANNELS:

                join_buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📢 {channel['name']}",
                            url=channel["link"]
                        )
                    ]
                )

            join_buttons.append(
                [
                    InlineKeyboardButton(
                        f"💬 {GROUP['name']}",
                        url=GROUP["link"]
                    )
                ]
            )

            join_buttons.append(
                [
                    InlineKeyboardButton(
                        "✅ DONE JOINING",
                        callback_data="check_join"
                    )
                ]
            )

            reply_markup = InlineKeyboardMarkup(join_buttons)

            await query.message.edit_text(
                "❌ AAPNE ABHI TAK SAB CHANNELS YA GROUP JOIN NAHI KIYE",
                reply_markup=reply_markup
            )

    # ======================================
    # MY INFO
    # ======================================

    elif query.data == "myinfo":

        tickets = await get_tickets(user_id)

        username = query.from_user.username

        if username:
            username = f"@{username}"
        else:
            username = query.from_user.first_name

        refer_link = (
            f"https://t.me/"
            f"{context.bot.username}"
            f"?start={user_id}"
        )

        buttons = [

            [
                InlineKeyboardButton(
                    "🔙 BACK",
                    callback_data="back"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            f"👤 USER: {username}\n\n"

            f"🎟️ TICKETS: {tickets}\n\n"

            f"🔗 REFER LINK:\n"
            f"{refer_link}",

            reply_markup=reply_markup
        )

    # ======================================
    # LEADERBOARD
    # ======================================

    elif query.data == "leaderboard":

        top_users = await get_top_users()

        text = "🏆 TOP 15 USERS\n\n"

        rank = 1

        for user in top_users:

            username = user[0]
            tickets = user[1]

            if not username:
                username = "Unknown User"

            text += (
                f"{rank}. {username} ➜ 🎟️ {tickets}\n"
            )

            rank += 1

        buttons = [

            [
                InlineKeyboardButton(
                    "🔙 BACK",
                    callback_data="back"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(
            text,
            reply_markup=reply_markup
        )

    # ======================================
    # BACK
    # ======================================

    elif query.data == "back":

        await open_main_menu(
            query.message,
            user_id
        )


# ==========================================
# HANDLERS
# ==========================================

def get_handlers():

    return [

        CommandHandler("start", start),

        CallbackQueryHandler(buttons)

    ]