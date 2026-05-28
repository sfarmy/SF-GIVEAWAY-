from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from database.db import (
    create_redeem_code,
    list_redeem_codes,
    get_all_users,
    get_redeem_users
)

ADMIN_IDS = [7305665779, 7331380618]


# ================= CHECK ADMIN =================
def is_admin(user_id):
    return user_id in ADMIN_IDS


# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    buttons = [
        [InlineKeyboardButton("🎁 Redeem System", callback_data="adm_redeem")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton("📨 Send User Msg", callback_data="adm_msg")]
    ]

    await update.message.reply_text(
        "👑 ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= ADMIN BUTTONS =================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query

    if not is_admin(q.from_user.id):
        return

    await q.answer()

    data = q.data

    # ================= REDEEM =================
    if data == "adm_redeem":

        text = (
            "🎁 REDEEM SYSTEM\n\n"
            "➕ CREATE CODE:\n"
            "/create CODE REWARD USES\n\n"
            "📋 LIST CODES:\n"
            "/list_redeem\n\n"
            "👤 CODE USERS:\n"
            "/redeem_users CODE"
        )

        await q.message.edit_text(text)
        return

    # ================= BROADCAST =================
    if data == "adm_broadcast":

        await q.message.edit_text(
            "📢 BROADCAST SYSTEM\n\n"
            "Use:\n"
            "/broadcast YOUR_MESSAGE"
        )
        return

    # ================= USER MSG =================
    if data == "adm_msg":

        await q.message.edit_text(
            "📨 USER MESSAGE SYSTEM\n\n"
            "Use:\n"
            "/msg USER_ID MESSAGE"
        )
        return


# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("❌ Send message also")
        return

    users = await get_all_users()

    sent = 0
    failed = 0

    for u in users:

        try:
            user_id = u[0]

            await context.bot.send_message(
                chat_id=user_id,
                text=text
            )

            sent += 1

        except:
            failed += 1

    await update.message.reply_text(
        f"✅ BROADCAST COMPLETED\n\n"
        f"📤 Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )


# ================= SEND USER MSG =================
async def msg_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:

        await update.message.reply_text(
            "❌ Format:\n/msg USER_ID MESSAGE"
        )
        return

    try:

        user_id = int(context.args[0])

        text = " ".join(context.args[1:])

        await context.bot.send_message(
            chat_id=user_id,
            text=text
        )

        await update.message.reply_text(
            "✅ MESSAGE SENT"
        )

    except:

        await update.message.reply_text(
            "❌ FAILED"
        )


# ================= CREATE REDEEM =================
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    try:

        code = context.args[0]
        reward = int(context.args[1])
        uses = int(context.args[2])

    except:

        await update.message.reply_text(
            "❌ Format:\n/create CODE REWARD USES"
        )
        return

    await create_redeem_code(
        code,
        reward,
        uses
    )

    await update.message.reply_text(
        f"✅ CODE CREATED\n\n"
        f"🎁 Code: {code}\n"
        f"🎟 Reward: {reward}\n"
        f"♻️ Uses: {uses}"
    )


# ================= LIST REDEEM =================
async def list_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    data = await list_redeem_codes()

    if not data:

        await update.message.reply_text(
            "❌ NO CODES"
        )
        return

    text = "🎁 ACTIVE REDEEM CODES\n\n"

    for c in data:

        text += (
            f"🎟 CODE: {c[0]}\n"
            f"💎 REWARD: {c[1]}\n"
            f"♻️ USES LEFT: {c[2]}\n\n"
        )

    await update.message.reply_text(text)


# ================= REDEEM USERS =================
async def redeem_users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 1:

        await update.message.reply_text(
            "❌ Format:\n/redeem_users CODE"
        )
        return

    code = context.args[0]

    users = await get_redeem_users(code)

    if not users:

        await update.message.reply_text(
            "❌ NO USERS FOUND"
        )
        return

    text = f"🎁 USERS WHO USED {code}\n\n"

    i = 1

    for u in users:

        username = u[0]

        if not username:
            username = "NO_USERNAME"

        text += f"{i}. {username}\n"

        i += 1

    await update.message.reply_text(text)


# ================= HANDLERS =================
def get_admin_handlers():

    return [

        CommandHandler(
            "admin",
            admin_panel
        ),

        CallbackQueryHandler(
            admin_buttons,
            pattern="^adm_"
        ),

        CommandHandler(
            "broadcast",
            broadcast
        ),

        CommandHandler(
            "msg",
            msg_user
        ),

        CommandHandler(
            "create",
            create
        ),

        CommandHandler(
            "list_redeem",
            list_redeem
        ),

        CommandHandler(
            "redeem_users",
            redeem_users
        )
    ]