import os
import json
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agentbuddy.session.client import SessionServiceClient
from agentbuddy.twin.client import TwinClient
from typing import Optional

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
    session.put_session_data(session_id=x_session_id, k="name",v="Emmanuele")
    session.put_session_data(session_id=x_session_id,k="short-description",v="SW Eng")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)