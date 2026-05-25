import aiosqlite
import time

DB_NAME = "database.db"


# ==========================================
# INIT DB
# ==========================================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            tickets INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            welcome_used INTEGER DEFAULT 0,
            referral_used INTEGER DEFAULT 0,
            last_bonus_day INTEGER DEFAULT 0
        )
        """)
        await db.commit()


# ==========================================
# ADD USER
# ==========================================
async def add_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (user_id, username, tickets)
        VALUES (?, ?, 0)
        """, (user_id, username))
        await db.commit()


# ==========================================
# GET TICKETS
# ==========================================
async def get_tickets(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT tickets FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0] if row else 0


# ==========================================
# TOP USERS
# ==========================================
async def top_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        SELECT username, tickets
        FROM users
        ORDER BY tickets DESC
        LIMIT 15
        """)
        return await cur.fetchall()


# ==========================================
# WELCOME BONUS (15 ONCE)
# ==========================================
async def give_welcome_bonus(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT welcome_used FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row or row[0] == 1:
            return False

        await db.execute("""
        UPDATE users
        SET tickets = tickets + 15,
            welcome_used = 1
        WHERE user_id=?
        """, (user_id,))

        await db.commit()
        return True


# ==========================================
# REFERRAL (ONE TIME ONLY)
# ==========================================
async def add_referral(referrer_id, user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("""
        SELECT referral_used, username
        FROM users
        WHERE user_id=?
        """, (user_id,))

        row = await cur.fetchone()

        if not row:
            return ("not_found", None)

        if row[0] == 1:
            return ("already", row[1])

        username = row[1]

        # lock referral
        await db.execute("""
        UPDATE users
        SET referral_used=1
        WHERE user_id=?
        """, (user_id,))

        # reward referrer
        await db.execute("""
        UPDATE users
        SET tickets = tickets + 10,
            referrals = referrals + 1
        WHERE user_id=?
        """, (referrer_id,))

        # reward user
        await db.execute("""
        UPDATE users
        SET tickets = tickets + 5
        WHERE user_id=?
        """, (user_id,))

        await db.commit()

        return ("success", username)


# ==========================================
# DAILY BONUS (RESET 12AM)
# ==========================================
def today():
    return int(time.time() // 86400)


async def claim_daily_bonus(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT last_bonus_day FROM users WHERE user_id=?",
            (user_id,)
        )

        row = await cur.fetchone()

        if not row:
            return False

        if row[0] == today():
            return "already"

        await db.execute("""
        UPDATE users
        SET tickets = tickets + 2,
            last_bonus_day = ?
        WHERE user_id=?
        """, (today(), user_id))

        await db.commit()

        return "success"