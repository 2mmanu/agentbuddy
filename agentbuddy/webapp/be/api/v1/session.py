import httpx
import os
import json
from typing import Optional
from fastapi import HTTPException, Header

SESSION_BASE_URL = os.getenv("SESSION_BASE_URL",default="http://localhost:8002/api/v1")

async def validate_session(x_session_id: Optional[str] = Header(None)) -> str:
    if not x_session_id:
        raise HTTPException(status_code=401, detail="Missing session ID")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SESSION_BASE_URL}/session-status", params={"session_id": x_session_id})
    
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session ID")
    
    return x_session_id


async def save_data_session(x_session_id,k,v):
    url = f"{SESSION_BASE_URL}/session-data"
    params = {"session_id": x_session_id, "k": k, "v": v}

    async with httpx.AsyncClient() as client:
        response = await client.put(url, params=params)
        return response.json()
        
def get_data_session(session_id,k):
    url = f"{SESSION_BASE_URL}/session-data"
    params = {"session_id": session_id, "k": k}
    with httpx.Client() as client:
        response = client.get(url, params=params)
        return response.json()