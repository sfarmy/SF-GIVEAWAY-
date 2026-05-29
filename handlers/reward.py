from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes
)


# ================= REWARDS MENU =================
async def rewards_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    q = update.callback_query

    await q.answer()

    text = """
🎁 AVAILABLE REWARDS

━━━━━━━━━━━━━━

🥇 TOP 1
🎁 Vice Cream NFT
🔗 https://t.me/nft/ViceCream-107913
👤 ADMIN: @rudrasocial

━━━━━━━━━━━━━━

🥈 TOP 2
🎁 Instant Ramen NFT
🔗 https://t.me/nft/InstantRamen-16371
👤 ADMIN: @rudrasocial

━━━━━━━━━━━━━━

🥉 TOP 3
🎁 Chill Flame NFT
🔗 https://t.me/nft/ChillFlame-127571
👤 ADMIN: @Somani

━━━━━━━━━━━━━━

🏅 TOP 4
🪙 500 Telegram Stars
👤 ADMIN: @rudrasocial

━━━━━━━━━━━━━━

🎖 TOP 5
💎 Telegram Premium Gift
👤 ADMIN: @rudrasocial

━━━━━━━━━━━━━━

🚀 MORE REWARDS COMING SOON...
"""

    buttons = [

        [
            InlineKeyboardButton(
                "🔙 BACK",
                callback_data="back"
            )
        ]
    ]

    await q.message.edit_text(
        text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= HANDLERS =================
def get_reward_handlers():

    return [

        CallbackQueryHandler(
            rewards_menu,
            pattern="^rewards_menu$"
        )
    ]