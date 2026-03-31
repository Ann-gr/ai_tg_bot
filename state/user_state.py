from state.storage import load_data, save_data

user_state = load_data()

def get_user(user_id):
    return user_state.get(str(user_id), {})

def set_user(user_id, data):
    user_state[str(user_id)] = data
    save_data(user_state)