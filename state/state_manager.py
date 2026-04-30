from services.state_db import get_state_db, save_state_db
import copy

def resolve_ui_state(state):
        if not state.get("current_text_id"):
            return "EMPTY"

        if state.get("mode") == "qa":
            return "QA"

        if state.get("last_result"):
            return "RESULT"

        return "TEXT_LOADED"

class StateManager:

    DEFAULT_STATE = {
        "mode": "analysis",
        "params": {},
        "current_text_id": None,
        "last_result": None,
        "last_result_id": None,
        "result_view": "short",
        "ui_state": "EMPTY"
    }

    async def get_state(self, user_id):
        db_state = await get_state_db(user_id)

        state = copy.deepcopy(self.DEFAULT_STATE)

        if db_state:
            state.update(db_state)

        return state

    async def update_state(self, user_id, **kwargs):
        state = await self.get_state(user_id)

        state.update(kwargs)
            
        await save_state_db(user_id, state)