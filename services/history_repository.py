import uuid
from services.db import get_pool
async def save_analysis(user_id, text_id, mode, result):
    pool = await get_pool()
    analysis_id = str(uuid.uuid4())

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO analysis_results (id, user_id, text_id, mode, result)
            VALUES ($1, $2, $3, $4, $5)
            """,
            analysis_id,
            str(user_id),
            text_id,
            mode,
            result
        )
    return analysis_id

async def get_user_analysis(user_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, mode, result
            FROM analysis_results
            WHERE user_id = $1 AND is_visible = TRUE
            ORDER BY created_at DESC
            LIMIT 10
            """,
            str(user_id)
        )

    return rows

async def hide_all_analysis(user_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE analysis_results SET is_visible = FALSE WHERE user_id = $1",
            str(user_id)
        )

async def get_analysis_by_id(analysis_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT result FROM analysis_results WHERE id = $1",
            analysis_id
        )

    return row["result"] if row else None

async def get_analysis_by_id_for_user(user_id, analysis_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, mode, result
            FROM analysis_results
            WHERE id = $1 AND user_id = $2
            """,
            analysis_id,
            str(user_id)
        )

    return row

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