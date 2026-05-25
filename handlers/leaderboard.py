handlers/leaderboard.py me ye FULL code daal 👇

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from database.db import top_users


# ==========================================
# LEADERBOARD SYSTEM
# ==========================================

async def open_leaderboard(query):

    users = await top_users()

    text = "🏆 TOP 15 USERS\n\n"

    count = 1

    for user in users:

        username = user[0]
        tickets = user[1]

        if not username:
            username = "Unknown User"

        text += (
            f"{count}. {username} "
            f"→ 🎟️ {tickets}\n"
        )

        count += 1

    buttons = [

        [
            InlineKeyboardButton(
                "🔙 BACK",
                callback_data="back"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(
        buttons
    )

    await query.message.edit_text(
        text,
        reply_markup=reply_markup
    )