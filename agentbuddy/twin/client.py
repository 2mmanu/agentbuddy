import httpx 

class TwinClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url)

    def send_message(self, session_id: str, content: str):
        url = "/send_message"
        data = {
            "session_id": session_id,
            "content": content
        }
        
        response = self.client.post(url, json=data, timeout=None)
        
        if response.status_code == 200:
            response_data = response.json()
            messages = response_data['messages']
            usage = response_data['usage']
            return messages, usage
        else:
            raise Exception(f"Failed to send message: {response.status_code}")

    def close(self):
        self.client.close()