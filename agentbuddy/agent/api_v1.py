from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx, tempfile, os, shutil
from agentbuddy.agent.base_agent import BaseAgent
from agentbuddy.agent.services.ask_to import ask_to
from agentbuddy.agent.services.verify import verify

network={
    "agents" : {}
}

purpose=os.getenv("AGENT_PURPOSE", default="")
hostname=os.getenv("AGENT_HOST", default="localhost")
port=os.getenv("AGENT_PORT", default="8080")
parent_hostname=os.getenv("AGENT_P_HOST", default=None)
parent_port=os.getenv("AGENT_P_PORT", default=None)
name=os.getenv("AGENT_NAME", default="generic")

def get_agent(session_id:str):

    agents = []
    for agent_name, agent in enumerate(network["agents"]):
        agents.append(
            f"you can ask to {agent_name} [at address {agent["hostname"]}:{agent["port"]}] about {agent["purpose"]}. use the function ask_to to send a question and get an answer. to try the connection you can use the function verify."
            )

    agent = BaseAgent(
        session_id=session_id, 
        agent_type=name, 
        human="", 
        persona=os.getenv("PERSONA_NAME", default="generic"),
        tools=[ask_to,verify], 
        memory_human="", 
        memory_persona=str(agents),
        )
    
    return agent

def notify_to_parent(name:str,purpose:str,hostname:str,port:str,parent_hostname:str,parent_port:str):
    notification_url = f"http://{parent_hostname}:{parent_port}/api/v1/new_agent"
    parameters = {"agent_name":name, "purpose":purpose, "hostname":hostname, "port":port}
    with httpx.Client() as client:
        response = client.put(notification_url, params=parameters)
        print(f"Notification sent with status code {response.status_code}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if parent_hostname is not None and parent_port is not None:
        notify_to_parent(name=name,purpose=purpose,hostname=hostname,port=port,parent_hostname=parent_hostname,parent_port=parent_port)
    yield
    # cleanup

app = FastAPI(lifespan=lifespan)

@app.get("/api/v1/ask")
def ask(question:str, session_id:str) -> str:
    agent = get_agent(session_id=session_id)
    if len(network["agents"])!=0:
        return str(agent.request(network["agents"],question))
    return str(agent.ask(question))

@app.get("/api/v1/verify")
def verify() -> str:
    return "OK"

@app.get("/api/v1/get_domains")
def get_domians(session_id:str) -> str:
    if len(network["agents"])!=0:
        agent = get_agent(session_id=session_id)
        #TODO questo dovrebbe essere fatto ogni volta che arriva un agente nuovo
        return str(agent.ask(question=f"Get a summary of the knowledge that you can access through the agents: {str(network['agents'])}. Do not give details about the names of the agents."))
    return "None"

@app.get("/api/v1/agents")
def list_agents() -> str:
    return str(network["agents"])

@app.put("/api/v1/new_agent")
def ask(agent_name:str, purpose:str, hostname:str, port:str,session_id:str) -> str:
    if agent_name not in network["agents"]:
        network["agents"][agent_name]={
            "purpose": purpose,
            "hostname": hostname,
            "port":port
        }
        return "OK"
    return f"agent {agent_name} exists"

@app.put("/api/v1/create_source")
def add_source(name,session_id:str):
    agent = get_agent(session_id=session_id)
    source_id = agent.create_source(name)
    return str(source_id)

@app.put("/api/v1/add_kb")
def add_kb(source_id:str, file: UploadFile,session_id:str) -> str:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            agent = get_agent(session_id=session_id)
            agent.add_file_to_source(source_id=source_id,filename=file_path)
            
            return JSONResponse(status_code=200, content={"message": "File uploaded and processed successfully"})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
