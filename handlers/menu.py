from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database.db import get_tickets


async def main_menu(message, user_id):

    tickets = await get_tickets(user_id)

    buttons = [
        [
            InlineKeyboardButton("👤 MY INFO", callback_data="myinfo"),
            InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("🎁 REDEEM CODE", callback_data="redeem")
        ],
        [
            InlineKeyboardButton("🎉 BONUS", callback_data="bonus")
        ]
    ]

    await message.reply_text(
        f"🎟️ SF GIVEAWAY PANEL\n\n🎫 YOUR TICKETS: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )