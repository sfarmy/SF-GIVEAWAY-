from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ==========================================
# BOT TOKEN
# ==========================================

TOKEN = "8830410554:AAFg8lg4tJM5P3u_xNYm0jhh7nwXeBuY-6E"

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

        # CHECK ALL CHANNELS
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
# START COMMAND
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    buttons = [
        [
            InlineKeyboardButton(
                "🎁 YOU ARE PARTICIPATE IN SF GIVEAWAY 🎁",
                callback_data="main"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ YES",
                callback_data="yes"
            ),

            InlineKeyboardButton(
                "❌ NO",
                callback_data="no"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "🔥 WELCOME TO SF GIVEAWAY 🔥",
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
    # NO BUTTON
    # ======================================

    if query.data == "no":

        buttons = [
            [
                InlineKeyboardButton(
                    "🎁 YOU ARE PARTICIPATE IN SF GIVEAWAY 🎁",
                    callback_data="main"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ YES",
                    callback_data="yes"
                ),

                InlineKeyboardButton(
                    "❌ NO",
                    callback_data="no"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(
            "⚠️ ARE YOU SURE ? ⚠️",
            reply_markup=reply_markup
        )

    # ======================================
    # YES BUTTON
    # ======================================

    elif query.data == "yes":

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
            "⚠️ JOIN ALL CHANNELS & GROUP TO PARTICIPATE ⚠️",
            reply_markup=reply_markup
        )

    # ======================================
    # FORCE JOIN CHECK
    # ======================================

    elif query.data == "check_join":

        joined = await check_force_join(
            user_id,
            context.bot
        )

        # SUCCESS
        if joined:

            await query.message.edit_text(
                "✅ SUCCESSFULLY JOINED ALL CHANNELS 🔥\n\n🎉 YOU ARE NOW PARTICIPATING IN SF GIVEAWAY"
            )

        # FAILED
        else:

            await query.answer(
                "⚠️ FIRST JOIN ALL CHANNELS & GROUP",
                show_alert=True
            )

# ==========================================
# MAIN BOT
# ==========================================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CallbackQueryHandler(buttons)
)

print("BOT RUNNING...")

app.run_polling()