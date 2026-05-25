from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database.db import *
import aiosqlite

ADMIN_IDS = [
    7305665779,
    7331380618
]
DB_NAME = "database.db"


# ================= CHECK ADMIN =================
def is_admin(user_id):
    return user_id in ADMIN_IDS


# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    buttons = [
        [InlineKeyboardButton("👤 User Management", callback_data="adm_user")],
        [InlineKeyboardButton("🎟 Redeem System", callback_data="adm_redeem")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton("✉️ Send User Msg", callback_data="adm_msg")]
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


    # ===== USER MENU =====
    if q.data == "adm_user":
        await q.message.edit_text(
            "👤 USER MANAGEMENT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Tickets", callback_data="add_t")],
                [InlineKeyboardButton("➖ Remove Tickets", callback_data="rem_t")],
                [InlineKeyboardButton("🚫 Ban User", callback_data="ban")],
                [InlineKeyboardButton("🔓 Unban User", callback_data="unban")]
            ])
        )


    # ===== REDEEM MENU =====
    elif q.data == "adm_redeem":
        await q.message.edit_text(
            "🎟 REDEEM SYSTEM",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Create Code", callback_data="create_code")],
                [InlineKeyboardButton("📋 Active Codes", callback_data="list_code")]
            ])
        )


    # ===== BROADCAST =====
    elif q.data == "adm_broadcast":
        await q.message.edit_text(
            "📢 Send message to ALL USERS\n\n(use /broadcast text)",
        )


    # ===== MESSAGE USER =====
    elif q.data == "adm_msg":
        await q.message.edit_text(
            "✉️ Send message to user\n\n(use /msg USER_ID text)",
        )


# ================= BROADCAST FUNCTION =================
async def broadcast(bot, text):

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        users = await cursor.fetchall()

        for u in users:
            try:
                await bot.send_message(u[0], text)
            except:
                pass


# ================= SEND MESSAGE TO USER =================
async def send_user_msg(bot, user_id, text):
    try:
        await bot.send_message(chat_id=user_id, text=text)
        return True
    except:
        return False


# ================= HANDLERS =================
def get_admin_handlers():
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_buttons)
    ]
