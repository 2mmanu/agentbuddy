import os
import requests
from agentbuddy.agent.base_agent import BaseAgent
from .services.facilitator import get_help


class Twin(BaseAgent):

    def __init__(self,
                 session_id:str,
                 tools:list = [get_help],
                 ) -> None:

        super().__init__(
                 session_id = session_id,
                 agent_type = "digital-twin",
                 human = "human",  
                 persona = "digital-twin",
                 tools=tools,
                 )
    
    def get_domains_syntax(self):
        address = os.getenv("FACILITATOR_BASE_URL", default="localhost:8888")
        api_url = f'http://{address}/api/v1/get_domains'
        response = requests.get(api_url)
        return response.json()
    
    def init_enterprise_context(self,user,domains):
        #TODO questo deve essere gestita con la memoria a lungo termine di memgpt
        question = f"""
        The name of the user is: {user}
        When the user asks a question about: [{domains}] use the function get_help if your knowledge is limited about the question. 
        The function can explain better about multiple domains. 
        Do not ask the user any questions until you have first consulted the get_help function.
        """
        self.send_message(question)