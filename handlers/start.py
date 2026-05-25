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

    reply_markup = InlineKeyboardMarkup(buttons)

    await message.edit_text(
        f"🎟️ WELCOME TO SF GIVEAWAY PANEL\n\n🎫 YOUR TICKETS: {tickets}",
        reply_markup=reply_markup
    )


# ==========================================
# START COMMAND (WITH REFERRAL SYSTEM)
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    username = f"@{user.username}" if user.username else user.first_name

    # referral
    referrer_id = None
    if context.args:
        try:
            referrer_id = int(context.args[0])
        except:
            pass

    # save user
    await add_user(user.id, username)

    # referral system
    if referrer_id and referrer_id != user.id:

        referred = await add_referral(referrer_id, user.id)

        if referred:

            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        f"🎉 NEW REFERRAL JOINED\n\n"
                        f"👤 USER: {username}\n"
                        f"🎟️ YOU GOT +10 TICKETS"
                    )
                )
            except:
                pass

            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=(
                        f"🎉 REFER BONUS RECEIVED\n\n"
                        f"🎟️ YOU GOT +5 TICKETS"
                    )
                )
            except:
                pass

    # greeting
    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1.5)

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

    reply_markup = InlineKeyboardMarkup(join_buttons)

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

    # CHECK JOIN
    if query.data == "check_join":

        await query.message.edit_text("🔍 CHECKING JOIN STATUS...")
        await asyncio.sleep(1)

        await query.message.edit_text("⚡ VERIFYING CHANNELS...")
        await asyncio.sleep(1)

        joined = await check_force_join(user_id, context.bot)

        if joined:

            await query.message.edit_text(
                "✅ VERIFIED SUCCESSFULLY 🔥\n\n🎉 YOU JOINED ALL CHANNELS & GROUP"
            )

            await asyncio.sleep(2)

            await open_main_menu(query.message, user_id)

        else:

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

            await query.message.edit_text(
                "❌ AAPNE ABHI TAK SAB CHANNELS YA GROUP JOIN NAHI KIYE",
                reply_markup=InlineKeyboardMarkup(join_buttons)
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

    # BONUS
    elif query.data == "bonus":

        claimed = await claim_bonus(user_id)

        if claimed:
            text = "🎉 DAILY BONUS CLAIMED\n\n🎟️ YOU GOT 2 TICKETS"
        else:
            text = "⚠️ YOU ALREADY CLAIMED TODAY BONUS"

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