from agentbuddy.agents.base import AgentBase
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool


class LangGraphAgent(AgentBase):
    def __init__(self, agent_id, tools=None, **kwargs):
        super().__init__(agent_id, tools, **kwargs)
        if 'provider' in kwargs:
            self.llm = self._load_llm(**kwargs)
        self.agent = self.create_base_agent()

    def _load_llm(self, **kwargs):
        provider = kwargs.get('provider')
        if provider.lower() == 'ollama':
            from langchain_ollama import ChatOllama
            return ChatOllama(**kwargs)
        else:
            raise ValueError(f"Provider {provider} non supportato.")

    def create_base_agent(self):
        tools = [ tool(fn) for fn in self.tools]
        model = self.llm

        return create_react_agent(model, tools)

    def interact(self, input_text):
        final_state = self.agent.invoke(
            {"messages": [{"role": "user", "content": input_text}]}
        )
        return final_state["messages"]