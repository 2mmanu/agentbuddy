from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from agentbuddy.agents import AgentFactory

class AgentCreateRequest(BaseModel):
    agent_type: str
    tools: list
    config: dict

class ChatRequest(BaseModel):
    message: str

app = FastAPI()

agents_db = {}

@app.post("/create_agent")
def create_agent(agent_config: AgentCreateRequest):
    """Crea un agente e assegnagli un ID"""
    agent_id = str(uuid.uuid4())
    
    try:
        params = {
            "agent_id": agent_id,
            "agent_type": agent_config.agent_type,
            "tools": [tool.name for tool in agent_config.tools],
            **agent_config.config,
        }

        agent = AgentFactory(**params)

        agents_db[agent_id] = params

        return {"message": f"Agent created successfully with ID {agent_id}.", "agent_id": agent_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating agent: {str(e)}")


@app.post("/chat/{agent_id}")
def chat_with_agent(agent_id: str, chat_request: ChatRequest):
    """Permette di inviare un messaggio all'agente e ricevere una risposta"""
    
    agent_params = agents_db.get(agent_id)
    
    if not agent_params:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        
        agent = AgentFactory(**agent_params)

        response = agent.interact(chat_request.message)

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error interacting with agent: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
