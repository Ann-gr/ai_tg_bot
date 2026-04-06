from state.db.connection import get_connection

def print_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_state")
    rows = cursor.fetchall()

    print("\n=== USER STATE ===")
    for row in rows:
        print(dict(row))

    conn.close()

def print_history(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute(
            "SELECT * FROM history WHERE user_id=? ORDER BY id DESC",
            (str(user_id),)
        )
    else:
        cursor.execute("SELECT * FROM history ORDER BY id DESC")

    rows = cursor.fetchall()

    print("\n=== HISTORY ===")
    for row in rows:
        print(dict(row))

    conn.close()

def print_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM user_state WHERE user_id=?",
        (str(user_id),)
    )

    row = cursor.fetchone()

    print("\n=== USER ===")
    print(dict(row) if row else "No data")

    conn.close()