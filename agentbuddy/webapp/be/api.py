import os
import json
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agentbuddy.session.client import SessionServiceClient
from agentbuddy.twin.client import TwinClient
from typing import Optional
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse
import uuid
import asyncio
from typing import Dict,List
from letta_client import Letta
from letta_client import MessageCreate, ReasoningMessage, AssistantMessage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session = SessionServiceClient(base_url=os.getenv("SESSION_BASE_URL",default="http://localhost:8002"))
twin = TwinClient(base_url=os.getenv("TWIN_BASE_URL",default="http://localhost:8005"))

@app.post("/api/v1/sentinel")
async def sentinel(x_session_id: Optional[str] = Header(None)):

    #TODO recupero delle informazioni utente da sistema e creazione oggetto di sessione
    username = os.getenv("USER_NAME", default="Emmanuele")
    short_desc = os.getenv("USER_SHORT", default="")
    session.put_session_data(session_id=x_session_id, k="name",v=username)
    session.put_session_data(session_id=x_session_id,k="short-description",v=short_desc)

    #TODO recupera il twin dell'utente e salvalo in sessione


    #TODO trigger per domini in facilitator
    # twin.get_domains_syntax()
    # await save_data_session(x_session_id=x_session_id, k="twin_domains", v=domains)
    # resp = twin.init_enterprise_context('Emmanuele',domains)
    return session.get_session(session_id=x_session_id)

@app.get("/api/v1/stream")
async def stream(sessionId: str, content: str):
    if not sessionId or not content:
        raise HTTPException(status_code=422, detail="Invalid parameters")

    # if not await validate_session(sessionId):
    #     raise HTTPException(status_code=401, detail="Invalid session ID")

    def event_generator():
        messages, usage = twin.send_message(session_id=sessionId, content=content)
        yield f"""data: {json.dumps({
            "messages": messages,
            "usage": usage,
            })
            }\n\n"""
        return

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Sessioni e action handlers
action_handlers: Dict[str, List[Dict[str, str]]] = {}  # {session_id: [{"id": "123", "name": "print_message"}]}
message_queues: Dict[str, asyncio.Queue] = {}

letta_client = Letta(base_url="http://localhost:8283")

# Storage dati (file/dict associati a session_id e action_id)
stored_data = {}


async def event_generator(session_id: str):
    """Generatore di eventi SSE."""
    while True:
        if session_id in message_queues:
            while not message_queues[session_id].empty():
                message = await message_queues[session_id].get()
                json_message = json.dumps(message, ensure_ascii=False)
                print(f"🔹 Inviando SSE: {json_message}")  # Debug
                yield f"data: {json_message}\n\n"  
        await asyncio.sleep(1)

@app.get("/stream/{session_id}")
async def stream(session_id: str):
    """API per avviare una connessione SSE."""
    if session_id not in message_queues:
        message_queues[session_id] = asyncio.Queue()
    return StreamingResponse(event_generator(session_id), media_type="text/event-stream")


@app.post("/register-actions/{session_id}")
async def register_actions(session_id: str, actions: List[Dict[str, str]]):
    """API per registrare le azioni supportate dal client."""
    if not isinstance(actions, list) or any("id" not in a or "name" not in a for a in actions):
        raise HTTPException(status_code=400, detail="Formato azioni non valido")

    action_handlers[session_id] = actions
    return {"status": "Actions registered", "actions": actions}


@app.post("/trigger-action/{session_id}")
async def trigger_action(session_id: str, action_id: str, params: dict):
    """API per inviare un evento di action al client, con parametri."""
    if session_id not in message_queues:
        raise HTTPException(status_code=404, detail="Sessione non trovata")

    # Verifica se l'azione è registrata dal client
    actions = action_handlers.get(session_id, [])
    matching_action = next((a for a in actions if a["id"] == action_id), None)
    
    if not matching_action:
        raise HTTPException(status_code=404, detail="Action non supportata dal client")

    action_name = matching_action["name"]
    message = {"type": "action", "action_id": action_id, "name": action_name, "params": params}

    await message_queues[session_id].put(message)
    return {"status": "Action triggered", "action_id": action_id, "name": action_name}


@app.post("/send-message/{session_id}")
async def send_message(session_id: str, message: Dict[str, str]):
    if session_id not in message_queues:
        raise HTTPException(status_code=404, detail="Sessione non trovata")

    user_message = message["text"]
    
    # Invia il messaggio originale al client
    await message_queues[session_id].put({"type": "chat", "user": message["user"], "text": user_message})

    # try:
    # Invia il messaggio a Letta
    response = letta_client.agents.messages.create(
        agent_id="agent-b6366c89-0e8a-4a40-8154-93bfd20ffdf4",
        messages=[MessageCreate(role="user", content=user_message)]
    )

    for message in response.messages:
        if type(message) == ReasoningMessage:
            await message_queues[session_id].put({"type": "chat", "user": "Reasoning", "text": message.reasoning})
        else:
            await message_queues[session_id].put({"type": "chat", "user": "Assistant", "text": message.content})

    return {"status": "Messaggio inviato a Letta"}

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Errore Letta: {str(e)}")

