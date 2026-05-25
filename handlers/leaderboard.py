
from database.db import top_users


async def leaderboard_text():

    users = await top_users()

    text = "🏆 TOP 15 USERS\n\n"

    count = 1

    for user in users:

        username = user[0]
        tickets = user[1]

        text += f"{count}. {username} → {tickets} 🎟️\n"

        count += 1

    return text
