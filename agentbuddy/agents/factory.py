from agentbuddy.agents.langgraph_agent import LangGraphAgent

class AgentFactory:
    _agent_classes = {
        "langgraph": LangGraphAgent
    }

    def __new__(cls, agent_type, agent_id, tools=None, **kwargs):
        agent_class = cls._agent_classes.get(agent_type)

        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return agent_class(
            agent_id=agent_id,
            tools=tools if tools else [],
            **kwargs
        )