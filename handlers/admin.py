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
    DB_NAME,
    add_tickets,
    remove_tickets,
    add_referrals,
    remove_referrals
)
import os
import shutil


# ================= ADMINS =================
ADMIN_IDS = [7305665779, 7331380618]

restore_state = {}
broadcast_state = {}
msg_state = {}

add_ticket_state = {}
remove_ticket_state = {}

add_ref_state = {}
remove_ref_state = {}

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
        "➕ Add Tickets",
        callback_data="adm_addtickets"
            )
        ],

        [
    InlineKeyboardButton(
        "➖ Remove Tickets",
        callback_data="adm_removetickets"
            )
        ],
        
        [
    InlineKeyboardButton(
        "👥 Add Referrals",
        callback_data="adm_addrefs"
            )
        ],

        [
    InlineKeyboardButton(
        "❌ Remove Referrals",
        callback_data="adm_removerefs"
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


# ================= CALLBACK BUTTONS =================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query

    if not is_admin(q.from_user.id):
        return

    await q.answer()

    data = q.data

    # ================= REDEEM =================
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


    if data == "adm_addtickets":

        add_ticket_state[q.from_user.id] = True

        await q.message.edit_text(
        "➕ SEND:\n\nUSER_ID TICKETS"
    )

        return


    if data == "adm_removetickets":

        remove_ticket_state[q.from_user.id] = True

        await q.message.edit_text(
        "➖ SEND:\n\nUSER_ID TICKETS"
    )

        return
        
        
    if data == "adm_addrefs":

        add_ref_state[q.from_user.id] = True

        await q.message.edit_text(
        "👥 SEND:\n\nUSER_ID REFERRALS"
    )

        return


    if data == "adm_removerefs":

        remove_ref_state[q.from_user.id] = True

        await q.message.edit_text(
        "❌ SEND:\n\nUSER_ID REFERRALS"
    )

        return

    # ================= BROADCAST =================
    if data == "adm_broadcast":

        broadcast_state[q.from_user.id] = True

        await q.message.edit_text(
            "📢 SEND MESSAGE FOR BROADCAST"
        )

        return

    # ================= SEND USER MSG =================
    if data == "adm_msg":

        msg_state[q.from_user.id] = True

        await q.message.edit_text(
            "📨 SEND:\n\nUSER_ID MESSAGE"
        )

        return

    # ================= BACKUP DB =================
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

    # ================= RESTORE DB =================
    if data == "adm_restore":

        restore_state[q.from_user.id] = True

        await q.message.edit_text(
            "♻️ SEND .db FILE\n\n⚠️ OLD DATA WILL BE REPLACED"
        )

        return


# ================= HANDLE RESTORE FILE =================
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

    # ================= BACKUP OLD DB =================
    if os.path.exists(DB_NAME):

        backup_path = DB_NAME + ".backup"

        shutil.copy(DB_NAME, backup_path)

    # ================= RESTORE =================
    await file.download_to_drive(DB_NAME)

    restore_state[user_id] = False

    await update.message.reply_text(
        "✅ DATABASE RESTORED\n\n📦 OLD BACKUP SAVED"
    )


# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    if not update.message:
        return

    user_id = update.effective_user.id

    text = update.message.text.strip()


    # ================= ADD TICKETS =================
    if add_ticket_state.get(user_id):

        try:

            uid, amount = text.split()

            await add_tickets(
                int(uid),
                int(amount)
            )

            await update.message.reply_text(
                f"✅ {amount} Tickets Added To {uid}"
            )

        except Exception as e:

            await update.message.reply_text(
                f"❌ ERROR:\n{e}"
            )

        add_ticket_state[user_id] = False

        return


    # ================= REMOVE TICKETS =================
    if remove_ticket_state.get(user_id):

        try:

            uid, amount = text.split()

            result = await remove_tickets(
                int(uid),
                int(amount)
            )

            if result == "user_not_found":

                await update.message.reply_text(
                    "❌ USER NOT FOUND"
                )

            else:

                await update.message.reply_text(
                    f"✅ {amount} Tickets Removed From {uid}"
                )

        except Exception as e:

            await update.message.reply_text(
                f"❌ ERROR:\n{e}"
            )

        remove_ticket_state[user_id] = False

        return
        
        # ================= ADD REFERRALS =================
    if add_ref_state.get(user_id):

        try:

            uid, amount = text.split()

            await add_referrals(
                int(uid),
                int(amount)
        )

            await update.message.reply_text(
            f"✅ {amount} Referrals Added To {uid}"
        )

        except Exception as e:

            await update.message.reply_text(
            f"❌ ERROR:\n{e}"
        )

        add_ref_state[user_id] = False

        return


# ================= REMOVE REFERRALS =================
    if remove_ref_state.get(user_id):

        try:

            uid, amount = text.split()

            result = await remove_referrals(
                int(uid),
                int(amount)
        )

            if result == "user_not_found":

                await update.message.reply_text(
                "❌ USER NOT FOUND"
            )

            else:

                await update.message.reply_text(
                f"✅ {amount} Referrals Removed From {uid}"
            )

        except Exception as e:

            await update.message.reply_text(
            f"❌ ERROR:\n{e}"
        )

        remove_ref_state[user_id] = False

        return

    # ================= BROADCAST =================
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

            except:
                failed += 1

        broadcast_state[user_id] = False

        await update.message.reply_text(
            f"✅ SENT: {sent}\n❌ FAILED: {failed}"
        )

        return
    
    
  


    # ================= BROADCAST =================
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

            except:
                failed += 1

        broadcast_state[user_id] = False

        await update.message.reply_text(
            f"✅ SENT: {sent}\n❌ FAILED: {failed}"
        )

        return

    # ================= SEND USER MESSAGE =================
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


# ================= CREATE REDEEM =================
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


# ================= LIST REDEEM =================
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


# ================= REDEEM USERS =================
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


# ================= HANDLERS =================
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
