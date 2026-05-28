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
        [InlineKeyboardButton("💾 Backup Database", callback_data="adm_backup")],
        [InlineKeyboardButton("♻️ Restore Database", callback_data="adm_restore")]
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


    # ================= REDEEM =================
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

        await q.message.edit_text("📢 /broadcast MESSAGE")
        return


    # ================= USER MSG =================
    if data == "adm_msg":

        await q.message.edit_text("📨 /msg USER_ID MESSAGE")
        return


    # ================= BACKUP =================
    if data == "adm_backup":

        if not os.path.exists(DB_NAME):
            await q.message.edit_text("❌ DB NOT FOUND")
            return

        await context.bot.send_document(
            chat_id=q.from_user.id,
            document=open(DB_NAME, "rb"),
            filename="database_backup.db"
        )

        await q.message.edit_text("✅ BACKUP SENT")
        return


    # ================= RESTORE =================
    if data == "adm_restore":

        restore_state[q.from_user.id] = True

        await q.message.edit_text("♻️ SEND .db FILE")
        return


# ================= RESTORE FILE =================
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
        await update.message.reply_text("❌ ONLY .db FILE")
        return

    file = await doc.get_file()
    await file.download_to_drive(DB_NAME)

    restore_state[user_id] = False

    await update.message.reply_text("✅ DATABASE RESTORED\nRESTART BOT")


# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("❌ SEND MESSAGE")
        return

    users = await get_all_users()

    sent = failed = 0

    for u in users:
        try:
            await context.bot.send_message(u[0], text)
            sent += 1
        except:
            failed += 1

    await update.message.reply_text(f"✅ SENT: {sent}\n❌ FAILED: {failed}")


# ================= MSG USER =================
async def msg_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ /msg USER_ID MESSAGE")
        return

    try:
        uid = int(context.args[0])
        msg = " ".join(context.args[1:])

        await context.bot.send_message(uid, msg)

        await update.message.reply_text("✅ SENT")

    except:
        await update.message.reply_text("❌ FAILED")


# ================= CREATE REDEEM =================
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    try:
        code = context.args[0]
        reward = int(context.args[1])
        uses = int(context.args[2])

        total_uses = uses

    except:
        await update.message.reply_text("❌ /create CODE REWARD USES")
        return

    await create_redeem_code(code, reward, uses, total_uses)

    await update.message.reply_text(
        f"✅ CREATED\n🎟 {code}\n💎 {reward}\n👥 {total_uses}"
    )


# ================= LIST REDEEM =================
async def list_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    data = await list_redeem_codes()

    if not data:
        await update.message.reply_text("❌ NO CODES")
        return

    text = "🎁 ACTIVE REDEEM CODES\n\n"

    for c in data:
        code, reward, uses_left, total_uses = c
        used = total_uses - uses_left

        text += (
            f"🎟 CODE: {code}\n"
            f"💎 REWARD: {reward}\n"
            f"👥 TOTAL: {total_uses}\n"
            f"✅ USED: {used}\n"
            f"♻️ LEFT: {uses_left}\n\n"
        )

    await update.message.reply_text(text)


# ================= REDEEM USERS (FIX DUPLICATE) =================
async def redeem_users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("❌ /redeem_users CODE")
        return

    code = context.args[0]
    users = await get_redeem_users(code)

    if not users:
        await update.message.reply_text("❌ NO USERS")
        return

    seen = set()
    text = f"🎁 USERS WHO USED {code}\n\n"

    i = 1

    for u in users:
        username = u[0] or "NO_USERNAME"

        if username in seen:
            continue

        seen.add(username)
        text += f"{i}. {username}\n"
        i += 1

    await update.message.reply_text(text)


# ================= HANDLERS =================
def get_admin_handlers():

    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_buttons, pattern="^adm_"),

        CommandHandler("broadcast", broadcast),
        CommandHandler("msg", msg_user),

        CommandHandler("create", create),
        CommandHandler("list_redeem", list_redeem),
        CommandHandler("redeem_users", redeem_users),

        MessageHandler(filters.Document.ALL, handle_restore_file)
    ]