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

import asyncio

# ==========================================
# BOT TOKEN
# ==========================================

TOKEN = "YOUR_NEW_BOT_TOKEN"

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