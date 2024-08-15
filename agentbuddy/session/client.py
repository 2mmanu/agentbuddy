import httpx

class SessionServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def create_session(self):
        url = f"{self.base_url}/api/v1/create-session"
        with httpx.Client() as client:
            response = client.post(url)
            response.raise_for_status()
            return response.json()

    def get_session(self, session_id: str):
        url = f"{self.base_url}/api/v1/session"
        with httpx.Client() as client:
            response = client.get(url, params={"session_id": session_id})
            response.raise_for_status()
            return response.json()

    def get_session_data(self, session_id: str, k: str):
        url = f"{self.base_url}/api/v1/session-data"
        with httpx.Client() as client:
            response = client.get(url, params={"session_id": session_id, "k": k})
            response.raise_for_status()
            return response.json()

    def put_session_data(self, session_id: str, k: str, v: str):
        url = f"{self.base_url}/api/v1/session-data"
        with httpx.Client() as client:
            response = client.put(url, params={"session_id": session_id, "k": k, "v": v})
            response.raise_for_status()
            return response.json()

    def put_agent_id(self, session_id: str, name: str, agent_id: str):
        url = f"{self.base_url}/api/v1/agent"
        with httpx.Client() as client:
            response = client.put(url, params={"session_id": session_id, "name": name, "id": agent_id})
            response.raise_for_status()
            return response.json()

    def get_agent_id(self, session_id: str, name: str):
        url = f"{self.base_url}/api/v1/agent"
        with httpx.Client() as client:
            response = client.get(url, params={"session_id": session_id, "name": name})
            response.raise_for_status()
            return response.json()

    def close_session(self, session_id: str):
        url = f"{self.base_url}/api/v1/close-session"
        with httpx.Client() as client:
            response = client.delete(url, json={"sessionId": session_id})
            response.raise_for_status()
            return response.json()


class ManagedSessionServiceClient(SessionServiceClient):
    def __init__(self, base_url: str, session_id:str ):
        super().__init__(base_url)
        self.session_id = session_id

    def initialize_session(self):
        session_info = self.create_session()
        self.session_id = session_info["sessionId"]

    def get_session(self):
        return super().get_session(self.session_id)

    def get_session_data(self, k: str):
        return super().get_session_data(self.session_id, k)

    def put_session_data(self, k: str, v: str):
        return super().put_session_data(self.session_id, k, v)

    def put_agent_id(self, name: str, agent_id: str):
        return super().put_agent_id(self.session_id, name, agent_id)

    def get_agent_id(self, name: str):
        return super().get_agent_id(self.session_id, name)

    def close_session(self):
        result = super().close_session(self.session_id)
        self.session_id = None
        return result