from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database.db import (
    create_redeem_code,
    list_redeem_codes,
    add_tickets,
    remove_tickets,
    ban_user,
    unban_user
)

import aiosqlite

DB_NAME = "database.db"


# ================= ADMINS =================
ADMIN_IDS = [7305665779, 7331380618]


def is_admin(user_id):
    return user_id in ADMIN_IDS


# ================= ENTRY PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    buttons = [
        [InlineKeyboardButton("🎁 Redeem System", callback_data="adm_redeem")],
        [InlineKeyboardButton("👤 User Management", callback_data="adm_user")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton("✉️ Send Message", callback_data="adm_msg")]
    ]

    await update.message.reply_text(
        "👑 ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= CALLBACK ROUTER =================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    if not is_admin(q.from_user.id):
        return

    data = q.data


    # ================= BACK =================
    if data == "back_admin":
        await admin_panel(update, context)
        return


    # ================= MAIN MENU =================
    if data == "adm_redeem":

        buttons = [
            [InlineKeyboardButton("➕ Create Code", callback_data="create_code")],
            [InlineKeyboardButton("📋 Active Codes", callback_data="list_code")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")]
        ]

        await q.message.edit_text("🎁 REDEEM SYSTEM", reply_markup=InlineKeyboardMarkup(buttons))


    elif data == "adm_user":

        buttons = [
            [InlineKeyboardButton("➕ Add Tickets", callback_data="add_t")],
            [InlineKeyboardButton("➖ Remove Tickets", callback_data="rem_t")],
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user")],
            [InlineKeyboardButton("🔓 Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")]
        ]

        await q.message.edit_text("👤 USER MANAGEMENT", reply_markup=InlineKeyboardMarkup(buttons))


    elif data == "adm_broadcast":

        await q.message.edit_text(
            "📢 BROADCAST MODE\n\nSend message:\n/broadcast your message",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")]
            ])
        )


    elif data == "adm_msg":

        await q.message.edit_text(
            "✉️ SEND MESSAGE MODE\n\nFormat:\n/msg USER_ID message",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")]
            ])
        )


    # ================= ACTION BUTTONS =================

    elif data == "create_code":
        await q.message.edit_text(
            "🎁 Create Code:\nUse:\n/create CODE REWARD USES",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_redeem")]
            ])
        )

    elif data == "list_code":

        codes = await list_redeem_codes()

        text = "📋 ACTIVE CODES\n\n"
        if not codes:
            text += "No codes found"
        else:
            for c in codes:
                text += f"🎁 {c[0]} | 🎟 {c[1]} | 🔁 {c[2]}\n"

        await q.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_redeem")]
            ])
        )

    elif data == "add_t":

        await q.message.edit_text(
            "➕ Add Tickets:\nUse:\n/add USER_ID AMOUNT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_user")]
            ])
        )

    elif data == "rem_t":

        await q.message.edit_text(
            "➖ Remove Tickets:\nUse:\n/remove USER_ID AMOUNT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_user")]
            ])
        )

    elif data == "ban_user":

        await q.message.edit_text(
            "🚫 Ban User:\nUse:\n/ban USER_ID",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_user")]
            ])
        )

    elif data == "unban_user":

        await q.message.edit_text(
            "🔓 Unban User:\nUse:\n/unban USER_ID",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="adm_user")]
            ])
        )


# ================= HANDLERS =================
def get_admin_handlers():
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_buttons)
    ]