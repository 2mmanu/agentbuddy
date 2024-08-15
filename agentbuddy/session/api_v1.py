from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .manager import SessionManager
from .basemodel import CloseSessionRequest


session_manager = SessionManager()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def check_session(session_id:str):
    if not session_manager.is_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/v1/create-session")
async def create_session():
    session_id = session_manager.create_session()
    return {"sessionId": session_id}

@app.get("/api/v1/session")
async def session_data(session_id: str):
    check_session(session_id)
    return session_manager.get_session(session_id)

@app.get("/api/v1/session-data")
async def get_session_data(session_id: str, k):
    check_session(session_id)
    return session_manager.get_session_data(session_id,"web",k)

@app.put("/api/v1/session-data")
async def put_session_data(session_id: str, k, v):
    check_session(session_id)
    session_manager.set_session_data(session_id,"web",k,v)

@app.put("/api/v1/agent")
async def put_agent_id(session_id: str, name, id):
    check_session(session_id)
    session_manager.set_session_data(session_id,"agents",name,id)

@app.get("/api/v1/agent")
async def get_agent_id(session_id: str, name):
    check_session(session_id)
    session_manager.get_session_data(session_id,"agents",name)

@app.delete("/api/v1/close-session")
async def close_session(request: CloseSessionRequest):
    session_id = request.sessionId
    check_session(session_id)
    session_manager.close_session(session_id)
    return {"status": "session closed"}