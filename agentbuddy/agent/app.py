import os
import uvicorn
from agentbuddy.agent.api_v1 import app

if __name__ == "__main__":
    port = int(os.getenv("AGENT_PORT", default="8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, workers=4)
