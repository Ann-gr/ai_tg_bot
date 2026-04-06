import asyncpg
import os

pool = None

async def connect_db():
    global pool

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not set in environment variables")

    pool = await asyncpg.create_pool(database_url)

    print("✅ PostgreSQL connected successfully")

async def get_pool():
    if pool is None:
        raise Exception("DB pool is not initialized")
    return pool