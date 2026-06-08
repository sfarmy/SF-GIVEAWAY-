import aiosqlite
import os
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "database.db")

# ================= IST TIME (NO PYTZ) =================
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

        # 🚀 PERFORMANCE INDEXES
        await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_tickets
        ON users(tickets)
        """)

        await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_redeem_used_user_code
        ON redeem_used(user_id, code)
        """)

        await db.commit()

# ================= TODAY (IST SAFE) =================
def get_today():
    return datetime.now(IST).strftime("%Y-%m-%d")


# ================= ADD USER =================
async def add_user(user_id, username):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:

            await db.execute("""
                INSERT INTO users (
                    user_id, username, tickets,
                    referrals, welcome_used,
                    referral_used, last_bonus_day,
                    is_banned
                )
                VALUES (?, ?, 0, 0, 0, 0, '', 0)
            """, (user_id, username))

            await db.commit()
            return True

        await db.execute(
            "UPDATE users SET username=? WHERE user_id=?",
            (username, user_id)
        )

        await db.commit()
        return False


# ================= GET TICKETS =================
async def get_tickets(user_id):

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT tickets FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0] if row else 0


# ================= GET REFERRALS =================
async def get_referrals(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT referrals FROM users WHERE user_id=?",
            (user_id,)
        )

        row = await cur.fetchone()

        return row[0] if row else 0


# ================= TOTAL USERS =================
async def get_total_users():

    async with aiosqlite.connect(DB_NAME) as db:
        
        cur = await db.execute("SELECT COUNT(*) FROM users")
        row = await cur.fetchone()
        return row[0]


# ================= TOTAL TICKETS =================
async def get_total_tickets():

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT SUM(tickets) FROM users")
        row = await cur.fetchone()
        return row[0] or 0


# ================= TOP USERS =================
async def top_users():

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
            SELECT username, tickets, referrals
            FROM users
            ORDER BY tickets DESC
            LIMIT 50
        """)
        return await cur.fetchall()


# ================= USER RANK =================
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


# ================= WELCOME BONUS =================
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


# ================= REFERRAL =================
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


# ================= DAILY BONUS =================
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


# ================= REDEEM SYSTEM =================
async def create_redeem_code(code, reward, uses, total_uses):

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR REPLACE INTO redeem_codes
            (code, reward, uses_left, total_uses)
            VALUES (?, ?, ?, ?)
        """, (code, reward, uses, total_uses))
        await db.commit()


async def list_redeem_codes():

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
            SELECT code, reward, uses_left, total_uses
            FROM redeem_codes
        """)
        return await cur.fetchall()


async def use_redeem_code(user_id, username, code):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT 1 FROM redeem_used WHERE user_id=? AND code=?",
            (user_id, code)
        )
        if await cur.fetchone():
            return "used"

        cur = await db.execute(
            "SELECT reward, uses_left FROM redeem_codes WHERE code=?",
            (code,)
        )
        row = await cur.fetchone()

        if not row:
            return "invalid"

        reward, uses_left = row

        if uses_left <= 0:
            return "expired"

        await db.execute(
            "UPDATE users SET tickets = tickets + ? WHERE user_id=?",
            (reward, user_id)
        )

        await db.execute(
            "UPDATE redeem_codes SET uses_left = uses_left - 1 WHERE code=?",
            (code,)
        )

        await db.execute(
            "INSERT INTO redeem_used (user_id, code) VALUES (?, ?)",
            (user_id, code)
        )

        await db.execute(
            "INSERT INTO redeem_logs (user_id, username, code) VALUES (?, ?, ?)",
            (user_id, username, code)
        )

        await db.commit()
        return reward


# ================= HELPERS =================
async def get_all_users():

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM users")
        return await cur.fetchall()


async def get_redeem_users(code):

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
            SELECT DISTINCT username, user_id
            FROM redeem_logs
            WHERE code=?
        """, (code,))
        return await cur.fetchall()


async def already_claimed_code(user_id, code):

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT 1 FROM redeem_used WHERE user_id=? AND code=?",
            (user_id, code)
        )
        return await cur.fetchone() is not None


async def save_claim_history(user_id, username, code):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT 1 FROM redeem_logs WHERE user_id=? AND code=?",
            (user_id, code)
        )

        if await cur.fetchone():
            return

        await db.execute(
            "INSERT INTO redeem_logs (user_id, username, code) VALUES (?, ?, ?)",
            (user_id, username, code)
        )

        await db.commit()
        
# ================= CLAIM REWARD =================

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
        """, (user_id,))

        await db.commit()

        return "success"