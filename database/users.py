import aiosqlite

from datetime import datetime


# ==========================================
# ADD USER
# ==========================================

async def add_user(user_id, username):

    async with aiosqlite.connect("database/data.db") as db:

        cursor = await db.execute(

            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        user = await cursor.fetchone()

        # USER NOT EXISTS
        if not user:

            await db.execute(

                """
                INSERT INTO users
                (
                    user_id,
                    username,
                    tickets,
                    invited_by,
                    join_date
                )

                VALUES (?, ?, ?, ?, ?)
                """,

                (
                    user_id,
                    username,
                    0,
                    0,
                    str(datetime.now())
                )
            )

            await db.commit()


# ==========================================
# GET USER
# ==========================================

async def get_user(user_id):

    async with aiosqlite.connect("database/data.db") as db:

        cursor = await db.execute(

            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        return await cursor.fetchone()


# ==========================================
# ADD TICKETS
# ==========================================

async def add_tickets(user_id, amount):

    async with aiosqlite.connect("database/data.db") as db:

        await db.execute(

            """
            UPDATE users
            SET tickets = tickets + ?
            WHERE user_id = ?
            """,

            (amount, user_id)
        )

        await db.commit()


# ==========================================
# GET TICKETS
# ==========================================

async def get_tickets(user_id):

    async with aiosqlite.connect("database/data.db") as db:

        cursor = await db.execute(

            """
            SELECT tickets
            FROM users
            WHERE user_id = ?
            """,

            (user_id,)
        )

        data = await cursor.fetchone()

        if data:
            return data[0]

        return 0
