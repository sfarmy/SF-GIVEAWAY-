import aiosqlite
import time
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "database.db")
BACKUP_FOLDER = os.path.join(BASE_DIR, "backups")


# ================= INIT DB =================
async def init_db():

    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            tickets INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            welcome_used INTEGER DEFAULT 0,
            referral_used INTEGER DEFAULT 0,
            last_bonus_day INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0
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


# ================= CREATE REDEEM =================
async def create_redeem_code(code, reward, uses, total_uses):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
            INSERT OR REPLACE INTO redeem_codes
            (code, reward, uses_left, total_uses)
            VALUES (?, ?, ?, ?)
        """, (code, reward, uses, total_uses))

        await db.commit()


# ================= LIST REDEEM =================
async def list_redeem_codes():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("""
            SELECT code, reward, uses_left, total_uses
            FROM redeem_codes
        """)

        return await cur.fetchall()


# ================= USE REDEEM =================
async def use_redeem_code(user_id, username, code):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("""
            SELECT *
            FROM redeem_used
            WHERE user_id=? AND code=?
        """, (user_id, code))

        if await cur.fetchone():
            return "used"

        cur = await db.execute("""
            SELECT reward, uses_left
            FROM redeem_codes
            WHERE code=?
        """, (code,))

        row = await cur.fetchone()

        if not row:
            return "invalid"

        reward, uses_left = row

        if uses_left <= 0:
            return "expired"

        await db.execute("""
            UPDATE users
            SET tickets = tickets + ?
            WHERE user_id=?
        """, (reward, user_id))

        await db.execute("""
            UPDATE redeem_codes
            SET uses_left = uses_left - 1
            WHERE code=?
        """, (code,))

        await db.execute("""
            INSERT INTO redeem_used (user_id, code)
            VALUES (?, ?)
        """, (user_id, code))

        await db.execute("""
            INSERT INTO redeem_logs (user_id, username, code)
            VALUES (?, ?, ?)
        """, (user_id, username, code))

        await db.commit()

        return reward


# ================= REDEEM USERS =================
async def get_redeem_users(code):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("""
            SELECT DISTINCT username, user_id
            FROM redeem_logs
            WHERE code=?
            ORDER BY rowid DESC
        """, (code,))

        return await cur.fetchall()


# ================= USERS =================
async def get_all_users():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("SELECT user_id FROM users")
        return await cur.fetchall()


# ================= TOP USERS =================
async def top_users():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("""
            SELECT username, tickets
            FROM users
            ORDER BY tickets DESC
            LIMIT 15
        """)

        return await cur.fetchall()