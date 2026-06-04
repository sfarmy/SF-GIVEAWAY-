from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes
)

async def rewards_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    q = update.callback_query

    await q.answer()

    text = """

🎬 𝑭𝑼𝑳𝑳 𝑬𝑿𝑷𝑳𝑨𝑵𝑨𝑻𝑰𝑶𝑵 + 𝑹𝑬𝑾𝑨𝑹𝑫 𝑹𝑬𝑽𝑬𝑨𝑳 🎁

━━━━━━━━━━━━━━━━━━

📺 𝑾𝒂𝒕𝒄𝒉 𝑻𝒉𝒆 𝑶𝒇𝒇𝒊𝒄𝒊𝒂𝒍 𝑽𝒊𝒅𝒆𝒐 𝑻𝒐 𝑲𝒏𝒐𝒘:

✨ 𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆 𝑮𝒊𝒗𝒆𝒂𝒘𝒂𝒚 𝑬𝒙𝒑𝒍𝒂𝒏𝒂𝒕𝒊𝒐𝒏
🎁 𝑭𝒖𝒍𝒍 𝑹𝒆𝒘𝒂𝒓𝒅 𝑹𝒆𝒗𝒆𝒂𝒍
🏆 𝑾𝒊𝒏𝒏𝒆𝒓 𝑫𝒊𝒔𝒕𝒓𝒊𝒃𝒖𝒕𝒊𝒐𝒏 𝑺𝒚𝒔𝒕𝒆𝒎
⚡ 𝑰𝒎𝒑𝒐𝒓𝒕𝒂𝒏𝒕 𝑮𝒊𝒗𝒆𝒂𝒘𝒂𝒚 𝑹𝒖𝒍𝒆𝒔

━━━━━━━━━━━━━━━━━━

🎬 𝑭𝒖𝒍𝒍 𝑬𝒙𝒑𝒍𝒂𝒏𝒂𝒕𝒊𝒐𝒏 + 𝑹𝒆𝒘𝒂𝒓𝒅 𝑹𝒆𝒗𝒆𝒂𝒍 👇

🔗 https://youtu.be/3ZV1OiTt-NM

━━━━━━━━━━━━━━━━━━

🦅 𝑺𝑭 𝑮𝑰𝑽𝑬𝑨𝑾𝑨𝒀 💓🤍
🎯 𝑭𝒂𝒊𝒓 • 𝑺𝒆𝒄𝒖𝒓𝒆 • 𝑻𝒓𝒂𝒏𝒔𝒑𝒂𝒓𝒆𝒏𝒕

"""

    buttons = [

    [
        InlineKeyboardButton(
            "🎬 𝑭𝑼𝑳𝑳 𝑬𝑿𝑷𝑳𝑨𝑵𝑨𝑻𝑰𝑶𝑵 + 𝑹𝑬𝑽𝑬𝑨𝑳",
            url="https://youtu.be/3ZV1OiTt-NM"
        )
    ],

    [
        InlineKeyboardButton(
            "🔙 𝑩𝑨𝑪𝑲 🏠",
            callback_data="back"
        )
    ]
]

    await q.message.edit_text(
        text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def get_reward_handlers():

    return [

        CallbackQueryHandler(
            rewards_menu,
            pattern="^rewards_menu$"
        )
    ]