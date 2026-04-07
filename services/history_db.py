from services.db import get_pool

async def add_message(user_id, role, content):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO history (user_id, role, content)
            VALUES ($1, $2, $3)
            """,
            str(user_id), role, content
        )

async def get_history(user_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content
            FROM history
            WHERE user_id = $1
            ORDER BY id DESC
            LIMIT 6
            """,
            str(user_id)
        )

    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]