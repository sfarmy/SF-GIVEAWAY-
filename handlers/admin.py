from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database.db import create_redeem_code, list_redeem_codes
import aiosqlite

ADMIN_IDS = [7305665779, 7331380618]


def is_admin(uid):
    return uid in ADMIN_IDS


# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    buttons = [
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
    uid = q.from_user.id

    if uid not in ADMIN_IDS:
        return

    await q.answer()
    data = q.data

    if data == "adm_redeem":
        await q.message.edit_text(
            "🎁 REDEEM SYSTEM\n\n"
            "➕ Create: /create CODE REWARD USES\n"
            "📋 List: /list_redeem"
        )
        return

    if data == "adm_broadcast":
        await q.message.edit_text(
            "📢 BROADCAST MODE\n\nUse:\n/broadcast your message"
        )
        return

    if data == "adm_msg":
        await q.message.edit_text(
            "✉️ USER MESSAGE MODE\n\nUse:\n/msg user_id message"
        )
        return


# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("❌ Message missing")
        return

    async with aiosqlite.connect("database.db") as db:
        cur = await db.execute("SELECT user_id FROM users")
        users = await cur.fetchall()

    sent = 0

    for u in users:
        try:
            await context.bot.send_message(chat_id=u[0], text=text)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {sent} users")


# ================= MSG USER =================
async def msg_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Format: /msg user_id message")
        return

    try:
        uid = int(context.args[0])
        text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=uid, text=text)
        await update.message.reply_text("✅ Sent")
    except:
        await update.message.reply_text("❌ Failed")


# ================= CREATE CODE =================
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    try:
        code = context.args[0]
        reward = int(context.args[1])
        uses = int(context.args[2])
    except:
        await update.message.reply_text("❌ Format: /create CODE REWARD USES")
        return

    await create_redeem_code(code, reward, uses)
    await update.message.reply_text(f"✅ Code Created: {code}")


# ================= LIST CODES =================
async def list_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    data = await list_redeem_codes()

    if not data:
        await update.message.reply_text("❌ No codes found")
        return

    text = "🎁 ACTIVE CODES\n\n"

    for c in data:
        text += f"{c[0]} | {c[1]} tickets | {c[2]} uses\n"

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
    ]