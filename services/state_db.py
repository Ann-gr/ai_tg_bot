import json
from services.db import get_pool

async def get_state_db(user_id):
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT mode, params, current_text_id, last_result_id
            FROM user_state
            WHERE user_id = $1
            """,
            str(user_id)
        )

    if not row:
        return {}

    return {
        "mode": row["mode"],
        "params": json.loads(row["params"] or "{}"),
        "current_text_id": row["current_text_id"],
        "last_result_id": row["last_result_id"]
    }


async def save_state_db(user_id, state):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_state (user_id, mode, params, current_text_id, last_result_id)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO UPDATE SET
                mode = EXCLUDED.mode,
                params = EXCLUDED.params,
                current_text_id = EXCLUDED.current_text_id,
                last_result_id = EXCLUDED.last_result_id
            """,
            str(user_id),
            state.get("mode"),
            json.dumps(state.get("params", {})),
            state.get("current_text_id"),
            state.get("last_result_id")
        )