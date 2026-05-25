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

        # CHECK CHANNELS
        for channel in CHANNELS:

            member = await bot.get_chat_member(
                channel["id"],
                user_id
            )

            if member.status in ["left", "kicked"]:
                return False

        # CHECK GROUP
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

async def open_main_menu(message):

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
        "🎟️ WELCOME TO SF GIVEAWAY PANEL",
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

    # CHANNEL BUTTONS
    for channel in CHANNELS:

        join_buttons.append(
            [
                InlineKeyboardButton(
                    f"📢 {channel['name']}",
                    url=channel["link"]
                )
            ]
        )

    # GROUP BUTTON
    join_buttons.append(
        [
            InlineKeyboardButton(
                f"💬 {GROUP['name']}",
                url=GROUP["link"]
            )
        ]
    )

    # DONE BUTTON
    join_buttons.append(
        [
            InlineKeyboardButton(
                "✅ DONE JOINING",
                callback_data="check_join"
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(join_buttons)

    # FINAL JOIN PANEL
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

        # LOADING EFFECT
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

            await open_main_menu(query.message)

        # FAILED
        else:

            join_buttons = []

            # CHANNEL BUTTONS
            for channel in CHANNELS:

                join_buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📢 {channel['name']}",
                            url=channel["link"]
                        )
                    ]
                )

            # GROUP BUTTON
            join_buttons.append(
                [
                    InlineKeyboardButton(
                        f"💬 {GROUP['name']}",
                        url=GROUP["link"]
                    )
                ]
            )

            # DONE BUTTON
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


# ==========================================
# HANDLERS
# ==========================================

def get_handlers():

    return [

        CommandHandler("start", start),

        CallbackQueryHandler(buttons)
  ]
