from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from database.db import (
    create_redeem_code,
    list_redeem_codes,
    get_all_users,
    get_redeem_users,
    DB_NAME
)

import os

ADMIN_IDS = [7305665779, 7331380618]

restore_state = {}
broadcast_state = {}
msg_state = {}


# ================= CHECK ADMIN =================
def is_admin(user_id):
    return user_id in ADMIN_IDS


# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    if not is_admin(update.effective_user.id):
        return

    buttons = [
        [InlineKeyboardButton("🎁 Redeem System", callback_data="adm_redeem")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton("📨 Send User Msg", callback_data="adm_msg")],
        [InlineKeyboardButton("💾 Backup DB", callback_data="adm_backup")],
        [InlineKeyboardButton("♻️ Restore DB", callback_data="adm_restore")]
    ]

    await update.message.reply_text(
        "👑 ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= CALLBACK =================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query

    if not is_admin(q.from_user.id):
        return

    await q.answer()
    data = q.data


    # ================= REDEEM INFO =================
    if data == "adm_redeem":
        await q.message.edit_text(
            "🎁 REDEEM SYSTEM\n\n"
            "➕ /create CODE REWARD USES\n"
            "📋 /list_redeem\n"
            "👤 /redeem_users CODE"
        )
        return


    # ================= BROADCAST =================
    if data == "adm_broadcast":
        broadcast_state[q.from_user.id] = True
        await q.message.edit_text("📢 SEND MESSAGE FOR BROADCAST")
        return


    # ================= MSG USER =================
    if data == "adm_msg":
        msg_state[q.from_user.id] = True
        await q.message.edit_text("📨 SEND: USER_ID MESSAGE")
        return


    # ================= BACKUP =================
    if data == "adm_backup":

        if not os.path.exists(DB_NAME):
            await q.message.edit_text("❌ DB NOT FOUND")
            return

        with open(DB_NAME, "rb") as f:
            await context.bot.send_document(
                chat_id=q.from_user.id,
                document=f,
                filename="database_backup.db"
            )

        await q.message.edit_text("✅ BACKUP SENT")
        return


    # ================= RESTORE =================
    if data == "adm_restore":
        restore_state[q.from_user.id] = True
        await q.message.edit_text("♻️ SEND .db FILE TO RESTORE (⚠️ OVERWRITES OLD DATA)")
        return


# ================= FILE RESTORE =================
async def handle_restore_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    if not restore_state.get(user_id):
        return

    doc = update.message.document

    if not doc or not doc.file_name.endswith(".db"):
        await update.message.reply_text("❌ ONLY .db FILE ALLOWED")
        return

    file = await doc.get_file()

    # SAFE BACKUP BEFORE RESTORE
    if os.path.exists(DB_NAME):
        os.rename(DB_NAME, DB_NAME + ".bak")

    await file.download_to_drive(DB_NAME)

    restore_state[user_id] = False

    await update.message.reply_text("✅ DATABASE RESTORED (OLD BACKUP SAVED)")


# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id
    text = update.message.text.strip()

    # ================= BROADCAST =================
    if broadcast_state.get(user_id):
        users = await get_all_users()

        sent = failed = 0

        for u in users:
            try:
                await context.bot.send_message(u[0], text)
                sent += 1
            except:
                failed += 1

        broadcast_state[user_id] = False
        await update.message.reply_text(f"✅ SENT: {sent}\n❌ FAILED: {failed}")
        return


    # ================= MSG USER =================
    if msg_state.get(user_id):

        try:
            uid, msg = text.split(" ", 1)

            await context.bot.send_message(int(uid), msg)

            await update.message.reply_text("✅ MESSAGE SENT")

        except:
            await update.message.reply_text("❌ FORMAT: USER_ID MESSAGE")

        msg_state[user_id] = False
        return


# ================= CREATE REDEEM =================
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    try:
        code = context.args[0]
        reward = int(context.args[1])
        uses = int(context.args[2])
    except:
        await update.message.reply_text("❌ /create CODE REWARD USES")
        return

    await create_redeem_code(code, reward, uses, uses)

    await update.message.reply_text("✅ REDEEM CREATED")


# ================= LIST REDEEM =================
async def list_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    data = await list_redeem_codes()

    text = "🎁 REDEEM CODES\n\n"

    for c in data:
        code, reward, uses_left, total_uses = c
        text += f"{code} | {reward} | LEFT:{uses_left}\n"

    await update.message.reply_text(text or "NO CODES")


# ================= REDEEM USERS =================
async def redeem_users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("❌ /redeem_users CODE")
        return

    users = await get_redeem_users(context.args[0])

    text = "🎁 USERS:\n\n"

    for u in users:
        text += f"{u[0]}\n"

    await update.message.reply_text(text or "NO USERS")


# ================= HANDLERS =================
def get_admin_handlers():

    return [
        CommandHandler("admin", admin_panel),

        CallbackQueryHandler(admin_buttons, pattern="^adm_"),

        CommandHandler("create", create),
        CommandHandler("list_redeem", list_redeem),
        CommandHandler("redeem_users", redeem_users),

        MessageHandler(filters.Document.ALL, handle_restore_file),
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
    ]