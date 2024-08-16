import httpx

class AgentClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def ask(self, question: str, session_id: str) -> str:
        response = httpx.get(f"{self.base_url}/api/v1/ask", params={"question": question, "session_id": session_id})
        response.raise_for_status()
        return response.text

    def verify(self) -> str:
        response = httpx.get(f"{self.base_url}/api/v1/verify")
        response.raise_for_status()
        return response.text

    def get_domains(self, session_id: str) -> str:
        response = httpx.get(f"{self.base_url}/api/v1/get_domains", params={"session_id": session_id})
        response.raise_for_status()
        return response.text

    def list_agents(self) -> str:
        response = httpx.get(f"{self.base_url}/api/v1/agents")
        response.raise_for_status()
        return response.text

    def add_agent(self, agent_name: str, purpose: str, hostname: str, port: str, session_id: str) -> str:
        response = httpx.put(f"{self.base_url}/api/v1/new_agent", params={
            "agent_name": agent_name,
            "purpose": purpose,
            "hostname": hostname,
            "port": port,
            "session_id": session_id
        })
        response.raise_for_status()
        return response.text

    def create_source(self, name: str, session_id: str) -> str:
        response = httpx.put(f"{self.base_url}/api/v1/create_source", params={"name": name, "session_id": session_id})
        response.raise_for_status()
        return response.text

    def add_kb(self, source_id: str, file_path: str, session_id: str) -> str:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = httpx.put(f"{self.base_url}/api/v1/add_kb", files=files, params={"source_id": source_id, "session_id": session_id})
            response.raise_for_status()
            return response.json().get("message")
