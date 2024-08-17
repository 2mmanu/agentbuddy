from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .twin import Twin
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    session_id: str
    content: str

class MessageResponse(BaseModel):
    messages: List[Dict[str, Any]]
    usage: Dict[str, Any]

@app.get("/api/v1/ask")
def ask(question:str, session_id:str) -> str:
    twin = Twin(session_id=session_id)
    return str(twin.about_me(question))

@app.post("/send_message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    twin = Twin(session_id=request.session_id)
    messages, usage = twin.send_message(question=request.content)
    
    return {
        "messages": messages,
        "usage": {
            "completion_tokens": usage.completion_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "total_tokens": usage.total_tokens,
            "step_count": usage.step_count,
        }
    }