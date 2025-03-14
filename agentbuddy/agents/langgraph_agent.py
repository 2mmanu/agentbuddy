from agentbuddy.agents.base import AgentBase
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate

class LangGraphAgent(AgentBase):
    def __init__(self, agent_id, tools=None, **kwargs):
        super().__init__(agent_id, tools, **kwargs)
        if 'provider' in kwargs:
            self.llm = self._load_llm(**kwargs)
        self.human = kwargs.get("human","")
        self.agent = self.create_base_agent()

    @staticmethod
    def _read_file(path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return f"[Errore: {path} non trovato]"
        except Exception as e:
            return f"[Errore durante la lettura di {path}: {e}]"
    
    @staticmethod
    def _make_prompt(base_path: str, buddy_path: str, human: str) -> str:
        base_content = LangGraphAgent._read_file(base_path)
        buddy_content = LangGraphAgent._read_file(buddy_path)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "#YOUR PERSONA#\n" + buddy_content),
            ("system", "#USER PROFILE#\n" + human),
            ("system", base_content),
            ("placeholder", "{messages}"),
        ])

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
        prompt = LangGraphAgent._make_prompt("agentbuddy/agents/prompts/base.txt", "agentbuddy/agents/prompts/buddy.txt", self.human)
        #print(prompt)
        agent = create_react_agent(model, tools, prompt=prompt)
        #print(agent.get_graph())
        return agent
        

    def interact(self, input_text):
        final_state = self.agent.invoke(
            {"messages": [{"role": "user", "content": input_text}]}
        )
        return final_state["messages"]