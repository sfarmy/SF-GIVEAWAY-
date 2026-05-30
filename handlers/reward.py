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

🎁 𝑮𝑰𝑭𝑻 𝑫𝑰𝑺𝑻𝑹𝑰𝑩𝑼𝑻𝑰𝑶𝑵 𝑺𝒀𝑺𝑻𝑬𝑴 🎁
━━━━━━━━━━━━━━━━━━━━━━━━
📌 𝑺𝒀𝑺𝑻𝑬𝑴 𝑶𝑽𝑬𝑹𝑽𝑰𝑬𝑾

🥇 𝟭 – 𝟱   ➝ 𝑴𝑨𝑰𝑵 𝑮𝑰𝑭𝑻𝑺 (𝑵𝑭𝑻 + 𝑾𝒉𝒂𝒕𝒔𝑨𝒑𝒑 𝑨𝒍𝒕)
🥈 𝟲 – 𝟭𝟬  ➝ 𝑺𝑷𝑬𝑪𝑰𝑨𝑳 𝑹𝑬𝑾𝑨𝑹𝑫𝑺
🥉 𝟭𝟭 – 𝟭𝟱 ➝ 𝑩𝑶𝑵𝑼𝑺 𝑮𝑰𝑭𝑻
🎯 𝟭𝟲 – 𝟯𝟬 ➝ 𝑪𝑯𝑶𝑰𝑪𝑬 𝑹𝑬𝑾𝑨𝑹𝑫
━━━━━━━━━━━━━━━━━━━━━━━━
🥇 𝑹𝑨𝑵𝑲 𝟭 – 𝟱 | 𝑴𝑨𝑰𝑵 𝑮𝑰𝑭𝑻𝑺

🎁 𝑬𝑨𝑪𝑯 𝑾𝑰𝑵𝑵𝑬𝑹 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑺:
✔ 𝑵𝑭𝑻 𝑹𝑬𝑾𝑨𝑹𝑫
✔ 📱 𝑾𝒉𝒂𝒕𝒔𝑨𝒑𝒑 𝑨𝒍𝒕𝒆𝒓𝒏𝒂𝒕𝒊𝒗𝒆 (@somani_07x)
━━━━━━━━━━━━━━━━━━━━━━━━
🥇 𝟭𝒔𝒕 𝑾𝑰𝑵𝑵𝑬𝑹
🎁 𝑵𝑭𝑻: 𝑫𝒆𝒔𝒌 𝑪𝒂𝒍𝒆𝒏𝒅𝒂𝒓
🔗 https://t.me/nft/DeskCalendar-211310
👤 𝑨𝒅𝒎𝒊𝒏: @annitheverifier
📱 𝑾𝑨 𝑨𝒍𝒕: @somani_07x
━━━━━━━━━━━━━━━━━━━━━━━━
🥈 𝟮𝒏𝒅 𝑾𝑰𝑵𝑵𝑬𝑹
🎁 𝑵𝑭𝑻: 𝑷𝒐𝒐𝒍 𝑭𝒍𝒐𝒂𝒕
🔗 https://t.me/nft/PoolFloat-72832
👤 𝑨𝒅𝒎𝒊𝒏: @ShadowEagleMM
📱 𝑾𝑨 𝑨𝒍𝒕: @somani_07x
━━━━━━━━━━━━━━━━━━━━━━━━
🥉 𝟯𝒓𝒅 𝑾𝑰𝑵𝑵𝑬𝑹
🎁 𝑵𝑭𝑻: 𝑪𝒉𝒊𝒍𝒍 𝑭𝒍𝒂𝒎𝒆
🔗 https://t.me/nft/ChillFlame-127571
👤 𝑨𝒅𝒎𝒊𝒏: @somani_07x
📱 𝑾𝑨 𝑨𝒍𝒕: @somani_07x
━━━━━━━━━━━━━━━━━━━━━━━━
🏅 𝟰𝒕𝒉 𝑾𝑰𝑵𝑵𝑬𝑹
🎁 𝑵𝑭𝑻: 𝑽𝒊𝒄𝒆 𝑪𝒓𝒆𝒂𝒎
🔗 https://t.me/nft/ViceCream-107913
👤 𝑨𝒅𝒎𝒊𝒏: @rudrasocial
📱 𝑾𝑨 𝑨𝒍𝒕: @somani_07x
━━━━━━━━━━━━━━━━━━━━━━━━
🎖 𝟱𝒕𝒉 𝑾𝑰𝑵𝑵𝑬𝑹
🎁 𝑵𝑭𝑻: 𝑿𝒎𝒂𝒔 𝑺𝒕𝒐𝒄𝒌𝒊𝒏𝒈
🔗 https://t.me/nft/XmasStocking-69840
👤 𝑨𝒅𝒎𝒊𝒏: @Relaxtations
📱 𝑾𝑨 𝑨𝒍𝒕: @somani_07x
━━━━━━━━━━━━━━━━━━━━━━━━
🥈 𝑹𝑨𝑵𝑲 𝟲 – 𝟭𝟬 | 𝑺𝑷𝑬𝑪𝑰𝑨𝑳 𝑹𝑬𝑾𝑨𝑹𝑫𝑺

𝟲𝒕𝒉  ➝ 𝑵𝑭𝑻 𝑰𝒏𝒔𝒕𝒂𝒏𝒕 𝑹𝒂𝒎𝒆𝒏
🔗 http://t.me/nft/InstantRamen-16371
𝟕𝒕𝒉  ➝ 𝟭.𝟮𝑲 𝑹𝒆𝒂𝒍 𝑺𝒖𝒃𝒔𝒄𝒓𝒊𝒃𝒆𝒓𝒔 (@zerotixzz)
𝟖𝒕𝒉  ➝ 𝟭.𝟮𝑲 𝑹𝒆𝒂𝒍 𝑺𝒖𝒃𝒔𝒄𝒓𝒊𝒃𝒆𝒓𝒔 (@zerotixzz)
𝟗𝒕𝒉  ➝ 𝑨𝑵𝑨𝑵𝑻-𝑿 𝑳𝒊𝒇𝒆𝒕𝒊𝒎𝒆 𝑨𝒄𝒄𝒆𝒔𝒔 (@Zyrox4og)
𝟭𝟬𝒕𝒉 ➝ 𝑺𝑯𝑨𝑺𝑻𝑹𝑨-𝑿 𝑳𝒊𝒇𝒆𝒕𝒊𝒎𝒆 𝑨𝒄𝒄𝒆𝒔𝒔 (𝑵𝑰𝑲)
━━━━━━━━━━━━━━━━━━━━━━━━
🥉 𝑹𝑨𝑵𝑲 𝟭𝟭 – 𝟭𝟱 | 𝑩𝑶𝑵𝑼𝑺 𝑮𝑰𝑭𝑻

📱 𝑻𝒆𝒍𝒆𝒈𝒓𝒂𝒎 𝑨𝒍𝒕𝒆𝒓𝒏𝒂𝒕𝒆 𝑨𝒄𝒄𝒐𝒖𝒏𝒕
👤 𝑷𝒓𝒐𝒗𝒊𝒅𝒆𝒅 𝒃𝒚: @somani_07x
━━━━━━━━━━━━━━━━━━━━━━━━
🎯 𝑹𝑨𝑵𝑲 𝟭𝟲 – 𝟯𝟬 | 𝑪𝑯𝑶𝑰𝑪𝑬 𝑹𝑬𝑾𝑨𝑹𝑫

✨ 𝑶𝒑𝒕𝒊𝒐𝒏 𝟭: 𝑨𝑵𝑨𝑵𝑻-𝑿 (𝟭 𝑴𝒐𝒏𝒕𝒉 𝑨𝒄𝒄𝒆𝒔𝒔)
🛡 𝑶𝒑𝒕𝒊𝒐𝒏 𝟮: 𝑺𝑯𝑨𝑺𝑻𝑹𝑨-𝑿 (𝟭 𝑴𝒐𝒏𝒕𝒉 𝑨𝒄𝒄𝒆𝒔𝒔)

⚠️ 𝑶𝒏𝒍𝒚 𝑶𝑵𝑬 𝑹𝒆𝒘𝒂𝒓𝒅 𝑷𝒆𝒓 𝑾𝒊𝒏𝒏𝒆𝒓

👤 𝑩𝒚: @shadowfighter05 | @proton_25
━━━━━━━━━━━━━━━━━━━━━━━━
🏁 𝑬𝑵𝑫 𝑶𝑭 𝑮𝑰𝑭𝑻 𝑫𝑰𝑺𝑻𝑹𝑰𝑩𝑼𝑻𝑰𝑶𝑵 𝑺𝒀𝑺𝑻𝑬𝑴

🦅  𝑺𝑭 𝑨𝑫𝑴𝑰𝑵𝑺 💓🤍
🎯 𝑶𝒇𝒇𝒊𝒄𝒊𝒂𝒍 𝑮𝒊𝒗𝒆𝒂𝒘𝒂𝒚 𝑻𝒆𝒂𝒎
⚡ 𝑭𝒂𝒊𝒓 • 𝑺𝒆𝒄𝒖𝒓𝒆 • 𝑻𝒓𝒂𝒏𝒔𝒑𝒂𝒓𝒆𝒏𝒕

"""

    buttons = [

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