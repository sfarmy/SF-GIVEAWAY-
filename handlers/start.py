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
    add_referral,
    claim_daily_bonus,
    give_welcome_bonus
)

import asyncio


# ==========================================
# CHANNELS
# ==========================================

CHANNELS = [
    {"name": "SF ARMY", "link": "https://t.me/+TwoCQG8QZPM1OGRl", "id": -1003689156772},
    {"name": "SF TOOL", "link": "https://t.me/anushar_file", "id": -1003746793908},
    {"name": "SF MM", "link": "https://t.me/EagleMiddleUpdates", "id": -1003971360634},
    {"name": "SF VOUCHER", "link": "https://t.me/eaglevoucher", "id": -1003770492772},
    {"name": "SF GIVEAWAY", "link": "https://t.me/sfgiveaways", "id": -1003664665551}
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
            InlineKeyboardButton("🎉 DAILY BONUS", callback_data="bonus")
        ]
    ]

    await message.edit_text(
        f"🎟️ WELCOME TO SF GIVEAWAY PANEL\n\n🎫 YOUR TICKETS: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================
# START COMMAND
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

    # welcome bonus (ONLY ONCE)
    welcome_msg = await give_welcome_bonus(user.id)

    # greeting
    msg = await update.message.reply_text(f"👋 HELLO {username}")

    await asyncio.sleep(1)
    await msg.edit_text("⚡ LOADING...")
    await asyncio.sleep(1)
    await msg.edit_text("🔍 CHECKING SYSTEM...")
    await asyncio.sleep(1)

    # join buttons
    join_buttons = []

    for c in CHANNELS:
        join_buttons.append([
            InlineKeyboardButton(f"📢 {c['name']}", url=c["link"])
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

    context.user_data["referrer_id"] = referrer_id


# ==========================================
# BUTTON HANDLER
# ==========================================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    # ==========================================
    # CHECK JOIN
    # ==========================================

    if query.data == "check_join":

        await query.message.edit_text("🔍 CHECKING JOIN STATUS...")
        await asyncio.sleep(1)

        joined = await check_force_join(user_id, context.bot)

        if not joined:
            await query.message.edit_text("❌ PLEASE JOIN ALL CHANNELS & GROUP FIRST")
            return

        await query.message.edit_text("✅ VERIFIED SUCCESSFULLY 🔥")

        # ==========================================
        # REFERRAL SYSTEM (ONLY AFTER JOIN)
        # ==========================================

        referrer_id = context.user_data.get("referrer_id")

        if referrer_id and referrer_id != user_id:

            result = await add_referral(referrer_id, user_id)

            if result == "success":

                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text="🎉 NEW USER JOINED\n🎟️ +10 TICKETS"
                    )
                except:
                    pass

                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="🎉 WELCOME BONUS RECEIVED\n🎟️ +5 TICKETS"
                    )
                except:
                    pass

            elif result == "already":

                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="⚠️ WELCOME BONUS ALREADY CLAIMED (ONE TIME ONLY)"
                    )
                except:
                    pass

        await asyncio.sleep(1)
        await open_main_menu(query.message, user_id)


    # ==========================================
    # MY INFO
    # ==========================================

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


    # ==========================================
    # LEADERBOARD
    # ==========================================

    elif query.data == "leaderboard":

        users = await top_users()

        text = "🏆 TOP USERS\n\n"

        i = 1
        for u in users:
            name = u[0] or "Unknown"
            text += f"{i}. {name} ➜ 🎟️ {u[1]}\n"
            i += 1

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )


    # ==========================================
    # DAILY BONUS
    # ==========================================

    elif query.data == "bonus":

        result = await claim_daily_bonus(user_id)

        if result == "success":
            text = "🎉 DAILY BONUS CLAIMED\n🎟️ +2 TICKETS"

        elif result == "already":
            text = "⚠️ YOU ALREADY CLAIMED TODAY BONUS\n⏳ COME BACK AFTER 12:00 AM"

        else:
            text = "❌ ERROR"

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )


    # ==========================================
    # BACK
    # ==========================================

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