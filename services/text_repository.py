import uuid
from services.db import get_pool

async def save_text(user_id, content):
    pool = await get_pool()
    text_id = str(uuid.uuid4())

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO texts (id, user_id, content)
            VALUES ($1, $2, $3)
            """,
            text_id, str(user_id), content
        )

    return text_id


async def get_text(text_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT content FROM texts WHERE id = $1",
            text_id
        )

    return row["content"] if row else None

async def save_chunks(text_id, chunks):
    pool = await get_pool()

    async with pool.acquire() as conn:
        for chunk in chunks:
            await conn.execute(
                """
                INSERT INTO text_chunks (id, text_id, content)
                VALUES ($1, $2, $3)
                """,
                str(uuid.uuid4()),
                text_id,
                chunk
            )

async def get_chunks(text_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT content FROM text_chunks WHERE text_id = $1",
            text_id
        )

    return [r["content"] for r in rows]