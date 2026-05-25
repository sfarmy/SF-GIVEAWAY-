import sqlite3


conn = sqlite3.connect(
    "database/database.db",
    check_same_thread=False
)

cursor = conn.cursor()


# ==========================================
# CREATE TABLE
# ==========================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    user_id INTEGER PRIMARY KEY,

    username TEXT,

    tickets INTEGER DEFAULT 0

)

""")

conn.commit()


# ==========================================
# ADD USER
# ==========================================

async def add_user(user_id, username):

    cursor.execute(

        "SELECT * FROM users WHERE user_id=?",

        (user_id,)
    )

    user = cursor.fetchone()

    if not user:

        cursor.execute(

            "INSERT INTO users VALUES (?, ?, ?)",

            (user_id, username, 5)
        )

        conn.commit()


# ==========================================
# GET TICKETS
# ==========================================

async def get_tickets(user_id):

    cursor.execute(

        "SELECT tickets FROM users WHERE user_id=?",

        (user_id,)
    )

    data = cursor.fetchone()

    if data:
        return data[0]

    return 0


# ==========================================
# ADD TICKETS
# ==========================================

async def add_tickets(user_id, amount):

    current = await get_tickets(user_id)

    new_amount = current + amount

    cursor.execute(

        "UPDATE users SET tickets=? WHERE user_id=?",

        (new_amount, user_id)
    )

    conn.commit()


# ==========================================
# TOP USERS
# ==========================================

async def get_top_users():

    cursor.execute("""

    SELECT username, tickets

    FROM users

    ORDER BY tickets DESC

    LIMIT 15

    """)

    return cursor.fetchall()
