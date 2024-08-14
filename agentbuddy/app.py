import uvicorn
import os
from agentbuddy.agent.api import get_agent_app

app = get_agent_app(
    name=os.getenv("AGENT_NAME", default="generic"),
    persona=os.getenv("PERSONA_NAME", default="generic"),
    purpose=os.getenv("AGENT_PURPOSE", default=None),
    hostname=os.getenv("AGENT_HOST", default=None),
    port=os.getenv("AGENT_PORT", default=None),
    parent_hostname=os.getenv("AGENT_P_HOST", default=None),
    parent_port=os.getenv("AGENT_P_PORT", default=None),
    )

uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("AGENT_PORT", default="8080")), workers=1)