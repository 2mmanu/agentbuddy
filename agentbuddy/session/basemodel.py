from pydantic import BaseModel

class CloseSessionRequest(BaseModel):
    sessionId: str