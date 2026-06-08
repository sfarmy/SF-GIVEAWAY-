#START.PY (FULL UPDATED CODE)

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database.db import (
    add_user,
    get_tickets,
    top_users,
    add_referral,
    claim_daily_bonus,
    give_welcome_bonus,
    use_redeem_code,
    already_claimed_code,
    save_claim_history,
    get_all_users,
    get_total_tickets,
    get_user_rank,
    get_referrals
)

from handlers.reward import rewards_menu

import asyncio

CHANNELS = [
    {
        "name": "𝑆𝐹 𝐴𝑅𝑀𝑌 🛡️",
        "link": "https://t.me/+TwoCQG8QZPM1OGRl",
        "id": -1003689156772
    },
    {
        "name": "𝑆𝐹 𝐹𝐼𝐿𝐸 📁",
        "link": "https://t.me/anushar_file",
        "id": -1003746793908
    },
    {
        "name": "𝑆𝐹 𝑀𝑀 💰",
        "link": "https://t.me/EagleMiddleUpdates",
        "id": -1003971360634
    },
    {
        "name": "𝑆𝐹 𝑉𝑂𝑈𝐶𝐻𝐸𝑅 🎫",
        "link": "https://t.me/eaglevoucher",
        "id": -1003770492772
    },
    {
        "name": "𝑆𝐹 𝐺𝐼𝑉𝐸𝐴𝑊𝐴𝑌 🎁",
        "link": "https://t.me/sfgiveaways",
        "id": -1003664665551
    }
]

GROUP = {
    "name": "𝑆𝐹 𝑇𝑂𝑂𝐿 𝐺𝐶 🛠️",
    "link": "https://t.me/sftoolgc",
    "id": -1002708620916
}
GROUP2 = {
    "name": "𝑆𝐹 𝐺𝐼𝑉𝐸𝐴𝑊𝐴𝑌 𝐺𝐶 👥",
    "link": "https://t.me/annisera",
    "id": -1002759753827
}

user_state = {}

ADMIN_IDS = [7305665779, 7331380618]

async def check_force_join(user_id, bot):

    not_joined = []

    for c in CHANNELS:
        try:
            member = await bot.get_chat_member(c["id"], user_id)

            if member.status in ["left", "kicked"]:
                not_joined.append(c)

        except:
            not_joined.append(c)

    try:
        member = await bot.get_chat_member(GROUP["id"], user_id)

        if member.status in ["left", "kicked"]:
            not_joined.append(GROUP)

    except:
        not_joined.append(GROUP)
    try:
        member = await bot.get_chat_member(GROUP2["id"], user_id)

        if member.status in ["left", "kicked"]:
            not_joined.append(GROUP2)

    except:
        not_joined.append(GROUP2)

    return not_joined

def get_join_buttons(channels):

    buttons = []

    for c in channels:
        buttons.append([
            InlineKeyboardButton(
                f"📢 {c['name']}",
                url=c["link"]
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "𝑉𝐸𝑅𝐼𝐹𝑌 𝐴𝐶𝐶𝐸𝑆𝑆 ✅",
            callback_data="check_join"
        )
    ])

    return InlineKeyboardMarkup(buttons)

async def open_main_menu(message, user_id):

    tickets = await get_tickets(user_id)

    buttons = [

        [
            InlineKeyboardButton(
                "𝐌𝐘 𝐈𝐍𝐅𝐎 👤",
                callback_data="myinfo"
            ),

            InlineKeyboardButton(
                "𝐋𝐄𝐀𝐃𝐄𝐑𝐁𝐎𝐀𝐑𝐃 🏆",
                callback_data="leaderboard"
            )
        ],

        [
            InlineKeyboardButton(
                "𝐑𝐄𝐃𝐄𝐄𝐌 𝐂𝐎𝐃𝐄 🎁",
                callback_data="redeem"
            ),

            InlineKeyboardButton(
                "𝐃𝐀𝐈𝐋𝐘 𝐁𝐎𝐍𝐔𝐒 🎟",
                callback_data="bonus"
            )
        ],

        [
            InlineKeyboardButton(
                "𝐑𝐄𝐖𝐀𝐑𝐃𝐒 🧧",
                callback_data="rewards_menu"
            )
        ]
    ]

    await message.edit_text(
        f"""
🦅 𝑊𝑒𝑙𝑐𝑜𝑚𝑒 𝑇𝑜 𝑆𝐹 𝐺𝑖𝑣𝑒𝑎𝑤𝑎𝑦 𝑃𝑎𝑛𝑒𝑙 💓🤍
━━━━━━━━━━━━━━━━━━
🎫 𝑌𝑜𝑢𝑟 𝑇𝑖𝑐𝑘𝑒𝑡 ➤ {tickets}
━━━━━━━━━━━━━━━━━━
        """,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    is_new_user = await add_user(user.id, username)

    if is_new_user:
        for admin in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin,
                    f"""
🚀 𝑁𝐸𝑊 𝑈𝑆𝐸𝑅 𝑆𝑇𝐴𝑅𝑇𝐸𝐷 𝐵𝑂𝑇

👤 𝑁𝑎𝑚𝑒 : {user.first_name}
🔗 𝑈𝑠𝑒𝑟𝑛𝑎𝑚𝑒 : {username}
🆔 𝐼𝐷 : {user.id}
"""
                )
            except:
                pass

    # ✅ REFERRAL SAVE ONLY (NO REWARD HERE)
    if context.args:
        try:
            referrer_id = int(context.args[0])

            if referrer_id != user.id:
                user_state[user.id] = {
                    "referrer_id": referrer_id,
                    "referral_done": False
                }

        except:
            pass

    msg = await update.message.reply_text(
        f"🦅 𝐇𝐋𝐋𝐋𝐎 {username} 💓🤍"
    )

    await asyncio.sleep(1)

    await msg.edit_text("🦅 𝐋𝐎𝐀𝐃𝐈𝐍𝐆 𝐏𝐀𝐍𝐄𝐋.")
    await asyncio.sleep(0.5)

    await msg.edit_text("🦅 𝐋𝐎𝐀𝐃𝐈𝐍𝐆 𝐏𝐀𝐍𝐄𝐋..")
    await asyncio.sleep(0.5)

    await msg.edit_text("🦅 𝐋𝐎𝐀𝐃𝐈𝐍𝐆 𝐏𝐀𝐍𝐄𝐋...")
    await asyncio.sleep(1)

    await msg.edit_text(
        """
📢 𝐉𝐎𝐈𝐍 𝐀𝐋𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 & 𝐆𝐑𝐎𝐔𝐏
🔐 𝐓𝐇𝐄𝐍 𝐂𝐋𝐈𝐂𝐊 𝐕𝐄𝐑𝐈𝐅𝐘 ✅
""",
        reply_markup=get_join_buttons(CHANNELS + [GROUP, GROUP2])
    )
    
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user = q.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"

    await q.answer()

    data = q.data

    if data == "check_join":

        not_joined = await check_force_join(
            user_id,
            context.bot
        )

        if not_joined:
            await q.message.edit_text(
                "❌ 𝑭𝑰𝑹𝑺𝑻 𝑱𝑶𝑰𝑵 𝑨𝑳𝑳 𝑪𝑯𝑨𝑵𝑵𝑬𝑳𝑺 📢",
                reply_markup=get_join_buttons(not_joined)
            )
            return

        bonus = await give_welcome_bonus(user_id)

        if bonus == "success":
            await q.message.edit_text(
                "🎁 𝑊𝐸𝐿𝐶𝑂𝑀𝐸 𝐵𝑂𝑁𝑈𝑆 𝐶𝑅𝐸𝐷𝐼𝑇𝐸𝐷 +15 🏆✨"
            )

            await asyncio.sleep(1)

        # 🔥 REFERRAL SYSTEM
        state = user_state.get(user_id)

        if state:
            if not state.get("referral_done"):

                referrer_id = state.get("referrer_id")

                if referrer_id:

                    try:
                        result = await add_referral(referrer_id, user_id)

                        if result == "success":
                            await context.bot.send_message(
                                referrer_id,
                                f"""
🎉 𝑵𝑬𝑾 𝑹𝑬𝑭𝑬𝑹𝑹𝑨𝑳 𝑬𝑨𝑹𝑵𝑬𝑫 🏆✨

👤 𝑈𝑆𝐸𝑅: {user.first_name}
📛 𝑈𝑆𝐸𝑅𝑁𝐴𝑀𝐸: {username}
🆔 𝐼𝐷: {user.id}

🎫 +10 𝑇𝐼𝐶𝐾𝐸𝑇𝑆 🔥
"""
                            )
                    except Exception as e:
                        print(e)
                user_state[user_id]["referral_done"] = True

        await open_main_menu(q.message, user_id)
        return

    if data == "back":
        await open_main_menu(q.message, user_id)
        return
    
            
    if data == "myinfo":

        tickets = await get_tickets(user_id)

        referrals = await get_referrals(user_id)
        status = " 🕺🏻𝑄𝑈𝐴𝐿𝐼𝐹𝐼𝐸𝐷" if referrals >= 15 else "🙅🏻𝑁𝑂𝑇 𝑄𝑈𝐴𝐿𝐼𝐹𝐼𝐸𝐷"

        rank = await get_user_rank(user_id)

        ref_link = (
            f"https://t.me/"
            f"{context.bot.username}"
            f"?start={user_id}"
        )

        text = f"""
👤 𝐌𝐘 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃  📊
━━━━━━━━━━━━━━━━━━━━━━━
🆔 𝑈𝑆𝐸𝑅 𝐼𝐷 : {user_id}
🎟 𝑇𝐼𝐶𝐾𝐸𝑇𝑆 : {tickets}
👥 𝑇𝑂𝑇𝐴𝐿 𝑅𝐸𝐹𝐸𝑅𝑅𝐴𝐿𝑆 : {referrals}
🏅 𝑆𝑇𝐴𝑇𝑈𝑆 : {status}
📊 𝑅𝐴𝑁𝐾 : #{rank}
━━━━━━━━━━━━━━━━━━━━━━━
🔗 𝑹𝑬𝑭𝑬𝑹𝑹𝑨𝑳 𝑳𝑰𝑵𝑲: {ref_link} 
        """

        await q.message.edit_text(
            text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 𝑩𝑨𝑪𝑲 🏠",
                        callback_data="back"
                    )
                ]
            ])
        )

        return

    if data == "leaderboard":

        users = await top_users()

        total_users = len(
        await get_all_users()
    )

        total_tickets = await get_total_tickets()

        rank = await get_user_rank(user_id)

        referrals = await get_referrals(user_id)

        status = (
        "🕺🏻𝑄𝑈𝐴𝐿𝐼𝐹𝐼𝐸𝐷"
        if referrals >= 15
        else "🙅🏻𝑁𝑂𝑇 𝑄𝑈𝐴𝐿𝐼𝐹𝐼𝐸𝐷"
    )

        text = f"""
🏆 𝑳𝑬𝑨𝑫𝑬𝑹𝑩𝑶𝑨𝑹𝑫 📊🔥
━━━━━━━━━━━━━━━━━━━━━━━
👥 𝑈𝑠𝑒𝑟𝑠 : {total_users}
🎟 𝑇𝑜𝑡𝑎𝑙 𝑇𝑖𝑐𝑘𝑒𝑡𝑠 : {total_tickets}
👥 𝑌𝑜𝑢𝑟 𝑅𝑒𝑓𝑒𝑟𝑟𝑎𝑙𝑠 : {referrals}
🏅 𝑆𝑇𝐴𝑇𝑈𝑆 : {status}
📊 𝑌𝑜𝑢𝑟 𝑅𝑎𝑛𝑘 : #{rank}
━━━━━━━━━━━━━━━━━━━━━━━
🔥 𝑻𝑶𝑷 50 𝑼𝑺𝑬𝑹𝑺 🏆
"""

        for i, u in enumerate(users, 1):

            name = u[0] or "Unknown"
            tickets = u[1]
            referrals = u[2]

            user_status = (
            "🕺🏻𝑄𝑈𝐴𝐿𝐼𝐹𝐼𝐸𝐷"
            if referrals >= 15
            else "🙅🏻𝑁𝑂𝑇 𝑄𝑈𝐴𝐿𝐼𝐹𝐼𝐸𝐷"
        )

            text += (
                f"{i}. {name}\n"
                f"🎟 𝑇𝐼𝐶𝐾𝐸𝑇𝑆 ➤ {tickets}\n"
                f"👥 𝑅𝐸𝐹𝐸𝑅𝑅𝐴𝐿𝑆 ➤ {referrals}\n"
                f"🏅 {user_status}\n\n"
        )

        await q.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 𝑩𝑨𝑪𝑲 🏠",
                    callback_data="back"
                )
            ]
        ])
    )

    
        return
    
    
    if data == "bonus":

        r = await claim_daily_bonus(user_id)

        txt = (
            "🎉 𝑩𝑶𝑵𝑼𝑺 𝑨𝑫𝑫𝑬𝑫 +2 𝑻𝑰𝑪𝑲𝑬𝑻𝑺 🏆✨"
            if r == "success"
            else "⚠️ 𝑩𝑶𝑵𝑼𝑺 𝑨𝑳𝑹𝑬𝑨𝑫𝒀 𝑪𝑳𝑨𝑰𝑴𝑬𝑫 ⏳\n\n🕒 𝑵𝑬𝑿𝑻 𝑩𝑶𝑵𝑼𝑺 𝑨𝑽𝑨𝑰𝑳𝑨𝑩𝑳𝑬 𝑻𝑶𝑴𝑶𝑹𝑹𝑶𝑾 🔥"
        )

        await q.message.edit_text(
            txt,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 𝑩𝑨𝑪𝑲 🏠",
                        callback_data="back"
                    )
                ]
            ])
        )

        return

    if data == "redeem":

        user_state[user_id] = "redeem"

        await q.message.edit_text(
            """
🎁 𝑬𝑵𝑻𝑬𝑹 𝒀𝑶𝑼𝑹 𝑹𝑬𝑫𝑬𝑬𝑴 𝑪𝑶𝑫𝑬 🎟️
💡 𝑪𝑳𝑨𝑰𝑴 𝒀𝑶𝑼𝑹 𝑹𝑬𝑾𝑨𝑹𝑫𝑺 𝑵𝑶𝑾 🚀
            """,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 𝑩𝑨𝑪𝑲 🏠",
                        callback_data="back"
                    )
                ]
            ])
        )

        return

    if data == "back":

        await open_main_menu(
            q.message,
            user_id
        )

        return

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    if not update.message:
        return

    user_id = update.effective_user.id

    text = update.message.text.strip()

    if user_state.get(user_id) == "redeem":

        username = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else update.effective_user.first_name
        )

        if await already_claimed_code(user_id, text):

            await update.message.reply_text(
                "❌ 𝑹𝑬𝑫𝑬𝑬𝑴 𝑪𝑶𝑫𝑬 𝑨𝑳𝑹𝑬𝑨𝑫𝒀 𝑼𝑺𝑬𝑫 \n\n🔁 𝑻𝑹𝒀 𝑨 𝑵𝑬𝑾 𝑪𝑶𝑫𝑬 𝑻𝑶 𝑪𝑳𝑨𝑰𝑴 𝑹𝑬𝑾𝑨𝑹𝑫𝑺 🎁🔥"
            )

            user_state[user_id] = None
            return

        result = await use_redeem_code(
            user_id,
            username,
            text
        )

        if result in ["invalid", "expired", "used"]:

            await update.message.reply_text(
                f"❌ {result.upper()}"
            )

        else:

            await save_claim_history(
                user_id,
                username,
                text
            )

            await update.message.reply_text(
                f"🎉 𝑹𝑬𝑫𝑬𝑬𝑴 𝑺𝑼𝑪𝑪𝑬𝑺𝑺𝑭𝑼𝑳 ✅🔥\n\n🎟️ +{result} 𝑻𝑰𝑪𝑲𝑬𝑻𝑺 𝑨𝑫𝑫𝑬𝑫 🏆✨"
            )

        user_state[user_id] = None

def get_handlers():

    return [

        CommandHandler(
            "start",
            start
        ),

        CallbackQueryHandler(
            buttons,
            pattern="^(check_join|myinfo|leaderboard|bonus|redeem|back)$"
        ),

        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    ]