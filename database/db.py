import aiosqlite
import time

DB_NAME = "database.db"


# ==========================================
# INIT DATABASE
# ==========================================

async def init_db():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (

                user_id INTEGER PRIMARY KEY,
                username TEXT,
                tickets INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0,
                last_bonus INTEGER DEFAULT 0

            )
            '''
        )

        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS referrals (

                referred_id INTEGER PRIMARY KEY,
                referrer_id INTEGER

            )
            '''
        )

        await db.commit()


# ==========================================
# ADD USER
# ==========================================

async def add_user(user_id, username):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        user = await cursor.fetchone()

        if not user:

            await db.execute(
                '''
                INSERT INTO users (
                    user_id,
                    username,
                    tickets,
                    referrals,
                    last_bonus
                )
                VALUES (?, ?, ?, ?, ?)
                ''',
                (user_id, username, 5, 0, 0)
            )

            await db.commit()


# ==========================================
# GET TICKETS
# ==========================================

async def get_tickets(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT tickets FROM users WHERE user_id = ?",
            (user_id,)
        )

        data = await cursor.fetchone()

        return data[0] if data else 0


# ==========================================
# TOP USERS
# ==========================================

async def top_users():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            '''
            SELECT username, tickets
            FROM users
            ORDER BY tickets DESC
            LIMIT 15
            '''
        )

        return await cursor.fetchall()


# ==========================================
# REFERRAL SYSTEM (FIXED)
# ==========================================

async def add_referral(referrer_id, user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT * FROM referrals WHERE referred_id = ?",
            (user_id,)
        )

        exists = await cursor.fetchone()

        if exists:
            return "already"

        await db.execute(
            '''
            INSERT INTO referrals (referred_id, referrer_id)
            VALUES (?, ?)
            ''',
            (user_id, referrer_id)
        )

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
# BONUS SYSTEM
# ==========================================

async def claim_bonus(user_id):

    today = int(time.time() // 86400)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT last_bonus FROM users WHERE user_id = ?",
            (user_id,)
        )

        data = await cursor.fetchone()

        if not data:
            return False

        if data[0] == today:
            return False

        await db.execute(
            '''
            UPDATE users
            SET tickets = tickets + 2,
                last_bonus = ?
            WHERE user_id = ?
            ''',
            (today, user_id)
        )

        await db.commit()

        return True