import uuid
from services.db import get_pool

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