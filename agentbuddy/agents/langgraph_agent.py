from agentbuddy.agents.base import AgentBase
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


class LangGraphAgent(AgentBase):
    def __init__(self, agent_id, tools=None, **kwargs):
        super().__init__(agent_id, tools, **kwargs)
        self.agent = self.create_base_agent()

    def create_base_agent(self):
        tools = [ tool(fn) for fn in self.tools]
        model = ChatOllama(model=self.model, temperature=0.7)

        return create_react_agent(model, tools)

    def interact(self, input_text):
        final_state = self.agent.invoke(
            {"messages": [{"role": "user", "content": input_text}]}
        )
        return final_state["messages"]