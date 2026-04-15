import uuid
from services.db import get_pool

async def save_qa(user_id, text_id, question, answer):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO qa_messages (id, user_id, text_id, question, answer)
            VALUES ($1, $2, $3, $4, $5)
            """,
            str(uuid.uuid4()),
            str(user_id),
            text_id,
            question,
            answer
        )

async def hide_all_qa(user_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE qa_messages SET is_visible = FALSE WHERE user_id = $1",
            str(user_id)
        )

async def get_user_qa(user_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, question, answer
            FROM qa_messages
            WHERE user_id = $1 AND is_visible = TRUE
            ORDER BY created_at DESC
            LIMIT 10
            """,
            str(user_id)
        )

    return rows