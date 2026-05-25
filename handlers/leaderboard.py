from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database.db import top_users


async def open_leaderboard(query):

    users = await top_users()

    text = "🏆 TOP 15 USERS\n\n"

    rank = 1

    for user in users:

        username = user[0] or "Unknown User"
        tickets = user[1]

        text += f"{rank}. {username} ➜ 🎟️ {tickets}\n"
        rank += 1

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 BACK", callback_data="back")]
        ])
    )