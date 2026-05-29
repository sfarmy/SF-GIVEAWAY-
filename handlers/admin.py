from telegram import (
Update,
InlineKeyboardButton,
InlineKeyboardMarkup
)

from telegram.ext import (
CommandHandler,
CallbackQueryHandler,
MessageHandler,
ContextTypes,
filters
)

from database.db import (
create_redeem_code,
list_redeem_codes,
get_all_users,
get_redeem_users,
DB_NAME
)

import os
import shutil

ADMIN_IDS = [7305665779, 7331380618]

restore_state = {}
broadcast_state = {}
msg_state = {}


def is_admin(user_id):
return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_chat.type != "private":
    return

if not is_admin(update.effective_user.id):
    return

buttons = [

    [
        InlineKeyboardButton(
            "🎁 Redeem System",
            callback_data="adm_redeem"
        )
    ],

    [
        InlineKeyboardButton(
            "📢 Broadcast",
            callback_data="adm_broadcast"
        )
    ],

    [
        InlineKeyboardButton(
            "📨 Send User Msg",
            callback_data="adm_msg"
        )
    ],

    [
        InlineKeyboardButton(
            "💾 Backup DB",
            callback_data="adm_backup"
        )
    ],

    [
        InlineKeyboardButton(
            "♻️ Restore DB",
            callback_data="adm_restore"
        )
    ]
]

await update.message.reply_text(
    "👑 ADMIN PANEL",
    reply_markup=InlineKeyboardMarkup(buttons)
)

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

q = update.callback_query

if not is_admin(q.from_user.id):
    return

await q.answer()

data = q.data

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

if data == "adm_broadcast":

    broadcast_state[q.from_user.id] = True

    await q.message.edit_text(
        "📢 SEND MESSAGE FOR BROADCAST"
    )

    return

if data == "adm_msg":

    msg_state[q.from_user.id] = True

    await q.message.edit_text(
        "📨 SEND:\n\nUSER_ID MESSAGE"
    )

    return

if data == "adm_backup":

    if not os.path.exists(DB_NAME):

        await q.message.edit_text(
            "❌ DATABASE NOT FOUND"
        )
        return

    await context.bot.send_document(
        chat_id=q.from_user.id,
        document=open(DB_NAME, "rb"),
        filename="database_backup.db"
    )

    await q.message.edit_text(
        "✅ DATABASE BACKUP SENT"
    )

    return

if data == "adm_restore":

    restore_state[q.from_user.id] = True

    await q.message.edit_text(
        "♻️ SEND .db FILE\n\n⚠️ OLD DATA WILL BE REPLACED"
    )

    return

async def handle_restore_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_chat.type != "private":
    return

user_id = update.effective_user.id

if not is_admin(user_id):
    return

if not restore_state.get(user_id):
    return


doc = update.message.document

if not doc:

    await update.message.reply_text(
        "❌ SEND .db FILE"
    )
    return


if not doc.file_name.endswith(".db"):

    await update.message.reply_text(
        "❌ ONLY .db FILE ALLOWED"
    )
    return


file = await doc.get_file()

if os.path.exists(DB_NAME):

    backup_path = DB_NAME + ".backup"

    shutil.copy(DB_NAME, backup_path)

await file.download_to_drive(DB_NAME)

restore_state[user_id] = False

await update.message.reply_text(
    "✅ DATABASE RESTORED\n\n📦 OLD BACKUP SAVED"
)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_chat.type != "private":
    return

if not update.message:
    return

user_id = update.effective_user.id

if not (
    broadcast_state.get(user_id)
    or msg_state.get(user_id)
):
    return

text = update.message.text.strip()

if broadcast_state.get(user_id):

    users = await get_all_users()

    sent = 0
    failed = 0

    for u in users:

        try:

            await context.bot.send_message(
                chat_id=u[0],
                text=text
            )

            sent += 1

        except Exception:
            failed += 1


    broadcast_state[user_id] = False

    await update.message.reply_text(
        f"✅ SENT: {sent}\n❌ FAILED: {failed}"
    )

    return


if msg_state.get(user_id):

    try:

        uid, msg = text.split(" ", 1)

        await context.bot.send_message(
            int(uid),
            msg
        )

        await update.message.reply_text(
            "✅ MESSAGE SENT"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ ERROR:\n{e}"
        )

    msg_state[user_id] = False

    return

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not is_admin(update.effective_user.id):
    return

try:

    code = context.args[0]
    reward = int(context.args[1])
    uses = int(context.args[2])

except:

    await update.message.reply_text(
        "❌ FORMAT:\n/create CODE REWARD USES"
    )

    return


await create_redeem_code(
    code,
    reward,
    uses,
    uses
)

await update.message.reply_text(
    f"✅ REDEEM CREATED\n\n"
    f"🎟 CODE: {code}\n"
    f"💎 REWARD: {reward}\n"
    f"👥 USES: {uses}"
)


async def list_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not is_admin(update.effective_user.id):
    return

data = await list_redeem_codes()

if not data:

    await update.message.reply_text(
        "❌ NO REDEEM CODES"
    )

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

async def redeem_users(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not is_admin(update.effective_user.id):
    return

if not context.args:

    await update.message.reply_text(
        "❌ /redeem_users CODE"
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

    username = u[0] or "NO_USERNAME"

    text += f"{i}. {username}\n"

    i += 1


await update.message.reply_text(text)


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
    ),

    MessageHandler(
        filters.Document.ALL,
        handle_restore_file
    ),

    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler,
        block=False
    )
]