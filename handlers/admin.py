from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import aiosqlite

DB_NAME = "database.db"

ADMIN_IDS = [7305665779, 7331380618]


def is_admin(user_id):
    return user_id in ADMIN_IDS


# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    buttons = [
        [InlineKeyboardButton("🎟 REDEEM CODES", callback_data="adm_redeem")],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="adm_broadcast")],
        [InlineKeyboardButton("✉️ SEND USER MSG", callback_data="adm_msg")]
    ]

    await update.message.reply_text(
        "👑 ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= CALLBACK =================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user_id = q.from_user.id

    if not is_admin(user_id):
        return

    await q.answer()

    data = q.data


    # ================= REDEEM MENU =================
    if data == "adm_redeem":

        await q.message.edit_text(
            "🎟 REDEEM SYSTEM",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ CREATE CODE", callback_data="create_code")],
                [InlineKeyboardButton("📋 LIST CODES", callback_data="list_code")]
            ])
        )


    # ================= BROADCAST =================
    elif data == "adm_broadcast":

        await q.message.edit_text(
            "📢 SEND BROADCAST\n\nType:\n/broadcast YOUR MESSAGE"
        )


    # ================= SEND USER MESSAGE =================
    elif data == "adm_msg":

        await q.message.edit_text(
            "✉️ SEND MESSAGE TO USER\n\nType:\n/msg USER_ID YOUR MESSAGE"
        )


# ================= BROADCAST COMMAND =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    text = " ".join(context.args)

    async with aiosqlite.connect(DB_NAME) as db:
        users = await db.execute("SELECT user_id FROM users")
        users = await users.fetchall()

        for u in users:
            try:
                await context.bot.send_message(u[0], text)
            except:
                pass

    await update.message.reply_text("✅ BROADCAST SENT")


# ================= SEND USER MESSAGE =================
async def msg_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    try:
        user_id = int(context.args[0])
        text = " ".join(context.args[1:])

        await context.bot.send_message(user_id, text)
        await update.message.reply_text("✅ MESSAGE SENT")

    except:
        await update.message.reply_text("❌ FORMAT: /msg USER_ID TEXT")


# ================= HANDLERS =================
def get_admin_handlers():
    return [
        CommandHandler("admin", admin_panel),
        CommandHandler("broadcast", broadcast),
        CommandHandler("msg", msg_user),
        CallbackQueryHandler(admin_buttons)
    ]