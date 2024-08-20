import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("AGENT_PORT", default="8080"))
    uvicorn.run("agentbuddy.agent.api_v1:app", host="0.0.0.0", port=port, workers=1)
