from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from database.db import (
    add_user,
    get_tickets,
    top_users,
    claim_bonus,
    add_referral
)

import asyncio


# ==========================================
# CHANNELS
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
        for channel in CHANNELS:
            member = await bot.get_chat_member(channel["id"], user_id)
            if member.status in ["left", "kicked"]:
                return False

        member = await bot.get_chat_member(GROUP["id"], user_id)
        if member.status in ["left", "kicked"]:
            return False

        return True

    except Exception as e:
        print(e)
        return False


# ==========================================
# MAIN MENU
# ==========================================

async def open_main_menu(message, user_id):

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

    await message.edit_text(
        f"🎟️ WELCOME TO SF GIVEAWAY PANEL\n\n🎫 YOUR TICKETS: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================
# START COMMAND (REFERRAL FIXED)
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    username = f"@{user.username}" if user.username else user.first_name

    # referral id
    referrer_id = None
    if context.args:
        try:
            referrer_id = int(context.args[0])
        except:
            pass

    # save user
    await add_user(user.id, username)

    # ==========================================
    # REFERRAL SYSTEM (FIXED BLOCK)
    # ==========================================

    if referrer_id and referrer_id != user.id:

        result = await add_referral(referrer_id, user.id)

        if result == "success":

            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text="🎉 NEW REFERRAL JOINED\n🎟️ +10 TICKETS"
                )
            except:
                pass

            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text="🎉 REFER BONUS RECEIVED\n🎟️ +5 TICKETS"
                )
            except:
                pass


        elif result == "already":

            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text="⚠️ REFERRAL ALREADY USED\n🎟️ BONUS ALREADY CLAIMED (ONE TIME ONLY)"
                )
            except:
                pass

    # ==========================================
    # WELCOME MESSAGE
    # ==========================================

    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1)

    await msg.edit_text("⚡ LOADING...")
    await asyncio.sleep(1)

    await msg.edit_text("🔍 CHECKING SYSTEM...")
    await asyncio.sleep(1)

    await msg.edit_text("📢 PREPARING CHANNELS...")
    await asyncio.sleep(1)

    # join buttons
    join_buttons = []

    for channel in CHANNELS:
        join_buttons.append([
            InlineKeyboardButton(f"📢 {channel['name']}", url=channel["link"])
        ])

    join_buttons.append([
        InlineKeyboardButton(f"💬 {GROUP['name']}", url=GROUP["link"])
    ])

    join_buttons.append([
        InlineKeyboardButton("✅ DONE JOINING", callback_data="check_join")
    ])

    await msg.edit_text(
        "⚠️ JOIN ALL CHANNELS & GROUP TO CONTINUE ⚠️",
        reply_markup=InlineKeyboardMarkup(join_buttons)
    )


# ==========================================
# CALLBACK HANDLER
# ==========================================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    # CHECK JOIN
    if query.data == "check_join":

        await query.message.edit_text("🔍 CHECKING JOIN STATUS...")
        await asyncio.sleep(1)

        await query.message.edit_text("⚡ VERIFYING CHANNELS...")
        await asyncio.sleep(1)

        joined = await check_force_join(user_id, context.bot)

        if joined:

            await query.message.edit_text(
                "✅ VERIFIED SUCCESSFULLY 🔥\n\n🎉 ALL CHANNELS JOINED"
            )

            await asyncio.sleep(1)

            await open_main_menu(query.message, user_id)

        else:

            await query.message.edit_text(
                "❌ PLEASE JOIN ALL CHANNELS FIRST"
            )

    # MY INFO
    elif query.data == "myinfo":

        tickets = await get_tickets(user_id)

        username = query.from_user.username
        username = f"@{username}" if username else query.from_user.first_name

        refer_link = f"https://t.me/{context.bot.username}?start={user_id}"

        await query.message.edit_text(
            f"👤 USER: {username}\n\n"
            f"🎟️ TICKETS: {tickets}\n\n"
            f"🔗 REFER LINK:\n{refer_link}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )

    # LEADERBOARD
    elif query.data == "leaderboard":

        users = await top_users()

        text = "🏆 TOP 15 USERS\n\n"

        rank = 1
        for u in users:
            name = u[0] or "Unknown User"
            tickets = u[1]
            text += f"{rank}. {name} ➜ 🎟️ {tickets}\n"
            rank += 1

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )

    # BONUS
    elif query.data == "bonus":

        claimed = await claim_bonus(user_id)

        if claimed:
            text = "🎉 DAILY BONUS CLAIMED\n🎟️ +2 TICKETS"
        else:
            text = "⚠️ ALREADY CLAIMED TODAY"

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )

    # BACK
    elif query.data == "back":
        await open_main_menu(query.message, user_id)


# ==========================================
# HANDLERS
# ==========================================

def get_handlers():
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(buttons)
    ]