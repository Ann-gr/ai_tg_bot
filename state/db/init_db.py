import sqlite3

DB_PATH = "tg_bot/state.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_state (
        user_id TEXT PRIMARY KEY,
        state TEXT
    )
    """)

    conn.commit()
    conn.close()