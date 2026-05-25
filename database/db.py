import aiosqlite

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

                referrals INTEGER DEFAULT 0

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
                INSERT INTO users(
                    user_id,
                    username,
                    tickets
                )

                VALUES(?, ?, ?)
                ''',

                (
                    user_id,
                    username,
                    5
                )
            )

            await db.commit()


# ==========================================
# GET USER
# ==========================================

async def get_user(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        return await cursor.fetchone()


# ==========================================
# GET TICKETS
# ==========================================

async def get_tickets(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT tickets FROM users WHERE user_id = ?",
            (user_id,)
        )

        user = await cursor.fetchone()

        if user:
            return user[0]

        return 0


# ==========================================
# ADD TICKETS
# ==========================================

async def add_tickets(user_id, amount):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(

            '''
            UPDATE users
            SET tickets = tickets + ?
            WHERE user_id = ?
            ''',

            (
                amount,
                user_id
            )
        )

        await db.commit()


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