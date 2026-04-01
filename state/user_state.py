from state.storage import load_data, save_data


# STATE (режимы, настройки)

def get_user(user_id):
    data = load_data()
    return data.get(str(user_id), {}).get("state", {})


def set_user(user_id, state):
    data = load_data()

    user = data.setdefault(str(user_id), {})
    user["state"] = state

    save_data(data)


# HISTORY (память диалога)

def add_message(user_id, role, content):
    data = load_data()

    user = data.setdefault(str(user_id), {})
    history = user.setdefault("history", [])

    history.append({
        "role": role,
        "content": content
    })

    user["history"] = history[-10:]  # ограничение

    save_data(data)


def get_history(user_id):
    data = load_data()
    return data.get(str(user_id), {}).get("history", [])

def clear_history(user_id):
    data = load_data()
    
    if str(user_id) in data:
        data[str(user_id)]["history"] = []

    save_data(data)