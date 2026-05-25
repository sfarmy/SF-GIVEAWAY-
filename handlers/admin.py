from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database.db import (
    create_redeem_code,
    list_redeem_codes
)

ADMIN_IDS = [7305665779, 7331380618]


def is_admin(uid):
    return uid in ADMIN_IDS


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    buttons = [
        [InlineKeyboardButton("🎁 Redeem System", callback_data="adm_redeem")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton("✉️ Send User Msg", callback_data="adm_msg")]
    ]

    await update.message.reply_text("👑 ADMIN PANEL", reply_markup=InlineKeyboardMarkup(buttons))


async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    uid = q.from_user.id

    if not is_admin(uid):
        return

    await q.answer()

    if q.data == "adm_redeem":
        await q.message.edit_text(
            "🎁 REDEEM SYSTEM\n\n/create CODE REWARD USES\n/list"
        )

    elif q.data == "adm_broadcast":
        await q.message.edit_text("📢 use /broadcast message")

    elif q.data == "adm_msg":
        await q.message.edit_text("✉️ use /msg user_id text")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    from database.db import DB_NAME
    import aiosqlite

    text = " ".join(context.args)

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM users")
        users = await cur.fetchall()

    for u in users:
        try:
            await context.bot.send_message(u[0], text)
        except:
            pass


async def msg_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    uid = int(context.args[0])
    text = " ".join(context.args[1:])

    await context.bot.send_message(uid, text)


def get_admin_handlers():
    return [
        CommandHandler("admin", admin_panel),
        CallbackQueryHandler(admin_buttons),
        CommandHandler("broadcast", broadcast),
        CommandHandler("msg", msg_user)
    ]