from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import asyncio

from database.db import (
    add_user, get_tickets, top_users, add_referral,
    claim_daily_bonus, give_welcome_bonus,
    use_redeem_code, already_claimed_code,
    save_claim_history, get_total_tickets,
    get_user_rank, get_referrals,
    get_available_milestones, claim_milestone,
    MILESTONE_REWARDS
)

from handlers.reward import rewards_menu

CHANNELS = [
    {"name": "𝑆𝐹 𝐴𝑅𝑀𝑌 🛡️", "link": "https://t.me/+TwoCQG8QZPM1OGRl", "id": -1003689156772},
    {"name": "𝑆𝐹 𝐹𝐼𝐿𝐸 📁", "link": "https://t.me/anushar_file", "id": -1003746793908},
]

GROUP = {"name": "𝑆𝐹 𝑇𝑂𝑂𝐿 𝐺𝐶 🛠️", "link": "https://t.me/sftoolgc", "id": -1002708620916}
GROUP2 = {"name": "𝑆𝐹 𝐺𝐼𝑉𝐸𝐴𝐰𝐀𝐘 𝐺𝐶 👥", "link": "https://t.me/annisera", "id": -1002759753827}

user_state = {}
ADMIN_IDS = [7305665779, 7331380618]


# ================= FORCE JOIN =================
async def check_force_join(user_id, bot):
    not_joined = []

    for c in CHANNELS + [GROUP, GROUP2]:
        try:
            member = await bot.get_chat_member(c["id"], user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(c)
        except:
            not_joined.append(c)

    return not_joined


def get_join_buttons(channels):
    buttons = [[InlineKeyboardButton(f"📢 {c['name']}", url=c["link"])] for c in channels]
    buttons.append([InlineKeyboardButton("VERIFY ✅", callback_data="check_join")])
    return InlineKeyboardMarkup(buttons)


# ================= MAIN MENU =================
async def open_main_menu(message, user_id):
    tickets = await get_tickets(user_id)

    buttons = [
        [
            InlineKeyboardButton("👤 MY INFO", callback_data="myinfo"),
            InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard"),
        ],
        [
            InlineKeyboardButton("🎁 REDEEM", callback_data="redeem"),
            InlineKeyboardButton("🎟 BONUS", callback_data="bonus"),
        ],
        [InlineKeyboardButton("🎯 MILESTONES", callback_data="milestones")],
        [InlineKeyboardButton("🧧 REWARDS", callback_data="rewards_menu")],
    ]

    await message.edit_text(
        f"🦅 WELCOME PANEL\n🎫 Tickets: {tickets}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    await add_user(user.id, username)

    msg = await update.message.reply_text("LOADING...")
    await asyncio.sleep(1)

    await msg.edit_text(
        "JOIN CHANNELS THEN VERIFY 👇",
        reply_markup=get_join_buttons(CHANNELS + [GROUP, GROUP2])
    )


# ================= CALLBACK HANDLER =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user_id = q.from_user.id
    username = f"@{q.from_user.username}" if q.from_user.username else "No Username"

    await q.answer()
    data = q.data


    # ---------------- CHECK JOIN ----------------
    if data == "check_join":
        not_joined = await check_force_join(user_id, context.bot)

        if not_joined:
            return await q.message.edit_text(
                "❌ JOIN ALL CHANNELS",
                reply_markup=get_join_buttons(not_joined)
            )

        await give_welcome_bonus(user_id)

        state = user_state.get(user_id)
        if state and not state.get("referral_done"):
            ref = state.get("referrer_id")

            if ref:
                await add_referral(ref, user_id)

            user_state[user_id]["referral_done"] = True

        return await open_main_menu(q.message, user_id)


    # ---------------- BACK ----------------
    if data == "back":
        return await open_main_menu(q.message, user_id)


    # ---------------- MY INFO ----------------
    if data == "myinfo":
        tickets = await get_tickets(user_id)
        refs = await get_referrals(user_id)
        rank = await get_user_rank(user_id)

        text = f"ID: {user_id}\nTickets: {tickets}\nRefs: {refs}\nRank: #{rank}"

        return await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data="back")]
            ])
        )


    # ---------------- LEADERBOARD ----------------
    if data == "leaderboard":
        users = await top_users() or []

        total_users = len(users)
        total_tickets = await get_total_tickets()
        rank = await get_user_rank(user_id)
        my_refs = await get_referrals(user_id)

        text = f"""
🏆 LEADERBOARD
Users: {total_users}
Tickets: {total_tickets}
Your Rank: #{rank}
Your Ref: {my_refs}
"""

        for i, u in enumerate(users, 1):
            text += f"\n{i}. {u[0]} | 🎟 {u[1]} | 👥 {u[2]}"

        return await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data="back")]
            ])
        )


    # ---------------- BONUS ----------------
    if data == "bonus":
        r = await claim_daily_bonus(user_id)

        txt = "BONUS +2 TICKETS" if r == "success" else "ALREADY CLAIMED"

        return await q.message.edit_text(
            txt,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data="back")]
            ])
        )


    # ---------------- REDEEM ----------------
    if data == "redeem":
        user_state[user_id] = {"mode": "redeem"}

        return await q.message.edit_text(
            "ENTER REDEEM CODE",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data="back")]
            ])
        )


    # ---------------- MILESTONES ----------------
    if data == "milestones":
        refs = await get_referrals(user_id)
        available = await get_available_milestones(user_id)

        if available:
            m = available[0]
            reward = MILESTONE_REWARDS.get(m, 0)

            text = f"Next: {m}\nReward: {reward}"

            keyboard = [
                [InlineKeyboardButton(f"CLAIM {m}", callback_data=f"claim_milestone:{m}")],
                [InlineKeyboardButton("BACK", callback_data="back")],
            ]
        else:
            text = f"No milestone\nRefs: {refs}"
            keyboard = [[InlineKeyboardButton("BACK", callback_data="back")]]

        return await q.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


    # ---------------- CLAIM MILESTONE ----------------
    if data.startswith("claim_milestone:"):
        m = int(data.split(":")[1])
        result = await claim_milestone(user_id, m)

        return await q.message.edit_text(
            f"Claimed: {m}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data="back")]
            ])
        )


# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_state.get(user_id, {}).get("mode") != "redeem":
        return

    if await already_claimed_code(user_id, text):
        user_state.pop(user_id, None)
        return await update.message.reply_text("ALREADY USED")

    result = await use_redeem_code(user_id, "user", text)

    await save_claim_history(user_id, "user", text)

    user_state.pop(user_id, None)
    await update.message.reply_text(f"SUCCESS +{result}")


# ================= HANDLERS =================
def get_handlers():
    return [
        CommandHandler("start", start),

        CallbackQueryHandler(
            buttons,
            pattern="^(check_join|myinfo|leaderboard|bonus|redeem|back|milestones|claim_milestone:\\d+)$"
        ),

        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler),
    ]