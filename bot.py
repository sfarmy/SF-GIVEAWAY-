from telegram.ext import ApplicationBuilder

from config import TOKEN

from handlers.start import get_handlers

from database.db import init_db

import asyncio


async def main():

    # DATABASE
    await init_db()

    # BOT
    app = ApplicationBuilder().token(TOKEN).build()

    # HANDLERS
    for handler in get_handlers():

        app.add_handler(handler)

    print("BOT RUNNING...")

    app.run_polling()


asyncio.run(main())
