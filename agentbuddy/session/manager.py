import uuid
from typing import Dict

class SessionManager:

    def __init__(self):
        self.sessions: Dict[str, dict] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "web": {},
            "agents": {},
        }
        return session_id
    
    def is_session(self, session_id:str) -> bool:
        return session_id in self.sessions

    def get_session(self, session_id: str) -> str:
        if session_id in self.sessions:
            return self.sessions.get(session_id)
        return None
    
    def set_session_data(self, session_id: str, session_type:str, k:str, v:str):
        if session_id in self.sessions:
            self.sessions[session_id][session_type][k]=v

    def get_session_data(self, session_id: str, session_type:str, k:str):
        if session_id in self.sessions:
            if k not in self.sessions[session_id][session_type]:
                return None
            return self.sessions[session_id][session_type][k]

    def close_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]