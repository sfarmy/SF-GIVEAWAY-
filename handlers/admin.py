from telegram import *
from telegram.ext import *
import aiosqlite

ADMIN_IDS = [7305665779, 7331380618]

DB_NAME = "database.db"


def is_admin(uid):
    return uid in ADMIN_IDS


async def admin_panel(update, context):

    if not is_admin(update.effective_user.id):
        return

    buttons = [
        [InlineKeyboardButton("User", callback_data="adm_user")],
        [InlineKeyboardButton("Redeem", callback_data="adm_redeem")],
        [InlineKeyboardButton("Broadcast", callback_data="adm_broadcast")]
    ]

    await update.message.reply_text("ADMIN PANEL", reply_markup=InlineKeyboardMarkup(buttons))


async def admin_buttons(update, context):

    q = update.callback_query
    uid = q.from_user.id

    if not is_admin(uid):
        return

    await q.answer()

    if q.data == "adm_redeem":
        await q.message.edit_text("REDEEM MENU")

    elif q.data == "adm_broadcast":
        await q.message.edit_text("USE /broadcast TEXT")

    elif q.data == "adm_user":
        await q.message.edit_text("USER PANEL")

    elif q.data == "adm_back":
        await admin_panel(update, context)


def get_admin_handlers():
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_buttons)
    ]