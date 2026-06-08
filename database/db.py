import aiosqlite
import os
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "database.db")

IST = timezone(timedelta(hours=5, minutes=30))


# ================= INIT DB =================
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
            last_bonus_day TEXT DEFAULT '',
            is_banned INTEGER DEFAULT 0,
            reward_claimed INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS redeem_codes (
            code TEXT PRIMARY KEY,
            reward INTEGER,
            uses_left INTEGER,
            total_uses INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS redeem_used (
            user_id INTEGER,
            code TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS redeem_logs (
            user_id INTEGER,
            username TEXT,
            code TEXT
        )
        """)

        await db.commit()


# ================= HELPERS =================
def get_today():
    return datetime.now(IST).strftime("%Y-%m-%d")


# ================= USER =================
async def add_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:
            await db.execute("""
                INSERT INTO users (user_id, username)
                VALUES (?, ?)
            """, (user_id, username))

            await db.commit()
            return True

        await db.execute(
            "UPDATE users SET username=? WHERE user_id=?",
            (username, user_id)
        )

        await db.commit()
        return False


# ================= BASIC GETTERS =================
async def get_tickets(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT tickets FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0] if row else 0


async def get_referrals(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT referrals FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0] if row else 0


async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM users")
        return await cur.fetchall()


async def get_total_tickets():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT SUM(tickets) FROM users")
        row = await cur.fetchone()
        return row[0] or 0


async def get_user_rank(user_id):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT tickets FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:
            return 0

        tickets = row[0]

        cur = await db.execute(
            "SELECT COUNT(*) FROM users WHERE tickets > ?",
            (tickets,)
        )
        higher = await cur.fetchone()

        return higher[0] + 1


# ================= REWARDS =================
async def give_welcome_bonus(user_id):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT welcome_used FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if row and row[0] == 1:
            return "already"

        await db.execute("""
            UPDATE users
            SET tickets = tickets + 15,
                welcome_used = 1
            WHERE user_id=?
        """, (user_id,))

        await db.commit()
        return "success"


async def add_referral(referrer_id, user_id):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT referral_used FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if row and row[0] == 1:
            return "already"

        await db.execute("""
            UPDATE users
            SET referral_used = 1
            WHERE user_id=?
        """, (user_id,))

        await db.execute("""
            UPDATE users
            SET tickets = tickets + 10,
                referrals = referrals + 1
            WHERE user_id=?
        """, (referrer_id,))

        await db.commit()
        return "success"


async def claim_daily_bonus(user_id):
    today = get_today()

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT last_bonus_day FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if row and row[0] == today:
            return "already"

        await db.execute("""
            UPDATE users
            SET tickets = tickets + 2,
                last_bonus_day = ?
            WHERE user_id=?
        """, (today, user_id))

        await db.commit()
        return "success"


# ================= QUALIFIED REWARD =================
async def claim_qualified_reward(user_id):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("""
            SELECT referrals, reward_claimed
            FROM users
            WHERE user_id=?
        """, (user_id,))

        row = await cur.fetchone()

        if not row:
            return "no_user"

        referrals, claimed = row

        if referrals < 15:
            return "not_eligible"

        if claimed == 1:
            return "already_claimed"

        await db.execute("""
            UPDATE users
            SET tickets = tickets + 250,
                reward_claimed = 1
            WHERE user_id=?
              AND reward_claimed = 0
        """, (user_id,))

        await db.commit()

        return "success"