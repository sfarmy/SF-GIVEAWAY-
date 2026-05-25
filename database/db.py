import aiosqlite
import time

DB_NAME = "database.db"


async def init_db():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            tickets INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            welcome_used INTEGER DEFAULT 0,
            referral_used INTEGER DEFAULT 0,
            last_bonus_day INTEGER DEFAULT 0
        )
        ''')

        await db.commit()


# ==========================================
# WELCOME BONUS (ONE TIME ONLY)
# ==========================================

async def give_welcome_bonus(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT welcome_used FROM users WHERE user_id = ?",
            (user_id,)
        )

        data = await cursor.fetchone()

        if not data or data[0] == 1:
            return False

        await db.execute(
            '''
            UPDATE users
            SET tickets = tickets + 15,
                welcome_used = 1
            WHERE user_id = ?
            ''',
            (user_id,)
        )

        await db.commit()

        return True


# ==========================================
# REFERRAL BONUS (ONE TIME ONLY)
# ==========================================

async def add_referral(referrer_id, user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT referral_used FROM users WHERE user_id = ?",
            (user_id,)
        )

        data = await cursor.fetchone()

        if not data or data[0] == 1:
            return "already"

        # lock referral
        await db.execute(
            "UPDATE users SET referral_used = 1 WHERE user_id = ?",
            (user_id,)
        )

        # rewards
        await db.execute(
            "UPDATE users SET tickets = tickets + 10 WHERE user_id = ?",
            (referrer_id,)
        )

        await db.execute(
            "UPDATE users SET tickets = tickets + 5 WHERE user_id = ?",
            (user_id,)
        )

        await db.commit()

        return "success"


# ==========================================
# DAILY BONUS (RESET 12 AM)
# ==========================================

def get_today():
    return int(time.time() // 86400)


async def claim_daily_bonus(user_id):

    today = get_today()

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT last_bonus_day FROM users WHERE user_id = ?",
            (user_id,)
        )

        data = await cursor.fetchone()

        if not data:
            return False

        last_day = data[0]

        # already claimed today
        if last_day == today:
            return "already"

        # update + reward
        await db.execute(
            '''
            UPDATE users
            SET tickets = tickets + 2,
                last_bonus_day = ?
            WHERE user_id = ?
            ''',
            (today, user_id)
        )

        await db.commit()

        return "success"