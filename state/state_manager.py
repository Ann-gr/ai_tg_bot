from state.db.repository import (
    get_state as db_get_state,
    save_state as db_save_state,
    add_history,
    get_history
)

class StateManager:
    """
    Единая точка доступа к состоянию пользователя
    """

    # STATE
    def get_state(self, user_id):
        state = db_get_state(user_id)
        return state or {
            "mode": "analysis",
            "params": {},
            "last_text": None,
            "last_result": None
        }

    def update_state(self, user_id, **kwargs):
        state = self.get_state(user_id)
        state.update(kwargs)
        db_save_state(user_id, state)

    # MODE
    def set_mode(self, user_id, mode):
        state = self.get_state(user_id)
        state["mode"] = mode
        db_save_state(user_id, state)

    def get_mode(self, user_id):
        return self.get_state(user_id).get("mode", "analysis")

    # PARAMS
    def set_params(self, user_id, params):
        state = self.get_state(user_id)
        state["params"] = params
        db_save_state(user_id, state)

    def get_params(self, user_id):
        return self.get_state(user_id).get("params", {})

    # TEXT
    def set_last_text(self, user_id, text):
        state = self.get_state(user_id)
        state["last_text"] = text
        db_save_state(user_id, state)

    def get_last_text(self, user_id):
        return self.get_state(user_id).get("last_text")

    # RESULT
    def set_last_result(self, user_id, result):
        state = self.get_state(user_id)
        state["last_result"] = result
        db_save_state(user_id, state)

    def get_last_result(self, user_id):
        return self.get_state(user_id).get("last_result")

    # HISTORY
    def add_message(self, user_id, role, content):
        add_history(user_id, role, content)

    def get_history(self, user_id, limit=10):
        return get_history(user_id, limit)