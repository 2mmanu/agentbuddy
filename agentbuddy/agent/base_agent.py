import os
from memgpt import create_client
from memgpt.memory import ChatMemory
from agentbuddy.session.client import ManagedSessionServiceClient

class BaseAgent():

    def __init__(self,
                 session_id:str,
                 agent_type:str,
                 human:str,  
                 persona:str,
                 tools:list,
                 memory_human:str = "",
                 memory_persona:str = "",
                 ) -> None:
        
        self._tools = tools

        self._client = self._get_memgpt_client()
        
        self._session = ManagedSessionServiceClient(base_url=os.getenv("SESSION_BASE_URL", default="http://localhost:8002"),session_id=session_id)

        #TODO move into twin
        if agent_type == "digital-twin":
            memory_human = f"""
            Name: {self._session.get_session_data("name")}
            {self._session.get_session_data("short-description")}
            """
            memory_persona="""
            Name: agentBuddy
            When the user asks a question use the function get_help if your knowledge is limited about the question. 
            The function can explain better about multiple domains. 
            Do not ask the user any questions until you have first consulted the get_help function.
            """

        self._agent_id = self._session.get_agent_id(agent_type)
        if not self._agent_id:
            self._persona = persona
            self._human = human
            self._agent_id = self._create_agent(human=memory_human,persona=memory_persona)
            self._session.put_agent_id(agent_type,self._agent_id)

    def get_agent_id(self):    
        return self._agent_id

    def _get_memgpt_client(self):
        _base_ulr = os.getenv("MEMGPT_BASE_URL", default="http://localhost:8083")
        _token = os.getenv("MEMGPT_KEY", default="sk-fa5c7de8d6c03bdb29a5efe5fe3fbacbdbd31fb341e4dccf")    
        return create_client(base_url=_base_ulr,token=_token)
    
    def _create_agent(self,human:str="",persona:str=""):
        tools = []
        for tool in self._tools:
            tools.append(self._client.create_tool(tool, tags=["extras"]).name)

        chatmemory = ChatMemory(
            human=human,
            persona=persona,
        )
        chatmemory.core_memory_append("human","")
        chatmemory.core_memory_append("persona","")
        
        _agent_client = self._client.create_agent(
            memory = chatmemory,
            metadata = {"human:": self._human, "persona": self._persona},
            tools=tools,
        )

        return _agent_client.id
    
    def send_message(self, question):
        _client = self._get_memgpt_client()
        response = _client.user_message(agent_id=self._agent_id, message=question)
        return response.messages, response.usage