from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database.db import get_user, add_tickets, get_tickets
import aiosqlite

# ================= ADMIN IDS =================
ADMIN_IDS = [7305665779, 7331380618]


def is_admin(user_id):
    return user_id in ADMIN_IDS


DB_NAME = "database.db"


# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ Not Authorized")
        return

    buttons = [
        [InlineKeyboardButton("👤 User Management", callback_data="adm_user")],
        [InlineKeyboardButton("🎁 Redeem System", callback_data="adm_redeem")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton("✉️ Send User Msg", callback_data="adm_msg")]
    ]

    await update.message.reply_text(
        "👑 ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= CALLBACK HANDLER =================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    user_id = q.from_user.id

    if not is_admin(user_id):
        await q.answer("Not allowed", show_alert=True)
        return

    await q.answer()


    # ===== USER MANAGEMENT =====
    if q.data == "adm_user":
        await q.message.edit_text(
            "👤 USER MANAGEMENT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Tickets", callback_data="add_t")],
                [InlineKeyboardButton("➖ Remove Tickets", callback_data="rem_t")],
                [InlineKeyboardButton("🚫 Ban (Coming)", callback_data="ban")],
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_back")]
            ])
        )


    # ===== REDEEM SYSTEM =====
    elif q.data == "adm_redeem":
        await q.message.edit_text(
            "🎁 REDEEM SYSTEM\n\n(Coming Fully Next Update)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_back")]
            ])
        )


    # ===== BROADCAST =====
    elif q.data == "adm_broadcast":
        await q.message.edit_text(
            "📢 BROADCAST MODE\n\nUse: /broadcast YOUR_MESSAGE",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_back")]
            ])
        )


    # ===== SEND MESSAGE =====
    elif q.data == "adm_msg":
        await q.message.edit_text(
            "✉️ SEND MESSAGE TO USER\n\nUse: /msg USER_ID MESSAGE",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_back")]
            ])
        )


    # ===== BACK =====
    elif q.data == "adm_back":
        await admin_panel(update, context)


# ================= BROADCAST =================
async def broadcast(bot, text):

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM users")
        users = await cur.fetchall()

        for u in users:
            try:
                await bot.send_message(u[0], text)
            except:
                pass


# ================= SEND MESSAGE =================
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