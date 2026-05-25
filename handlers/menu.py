
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


async def main_menu(message):

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

    await message.reply_text(
        "🎟️ SF GIVEAWAY PANEL",
        reply_markup=reply_markup
    )
