import json
from state.db.connection import get_connection

# STATE
def get_state(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_state WHERE user_id=?", (str(user_id),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {}

    return {
        "mode": row["mode"],
        "params": json.loads(row["params"] or "{}"),
        "last_text": row["last_text"],
        "last_result": row["last_result"],
    }


def save_state(user_id, state):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO user_state (user_id, mode, params, last_text, last_result)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        mode=excluded.mode,
        params=excluded.params,
        last_text=excluded.last_text,
        last_result=excluded.last_result
    """, (
        str(user_id),
        state.get("mode"),
        json.dumps(state.get("params", {})),
        state.get("last_text"),
        state.get("last_result"),
    ))

    conn.commit()
    conn.close()


# HISTORY
def add_history(user_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history (user_id, role, content)
    VALUES (?, ?, ?)
    """, (str(user_id), role, content))

    conn.commit()
    conn.close()

def get_history(user_id, limit=6):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, content FROM history
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT ?
    """, (str(user_id), limit))

    rows = cursor.fetchall()
    conn.close()

    return list(reversed(rows))