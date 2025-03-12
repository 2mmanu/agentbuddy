import unittest
from agentbuddy.agents  import AgentFactory
from agentbuddy.agents.langgraph_agent import LangGraphAgent

class TestAgentFactory(unittest.TestCase):
    
    def test_create_valid_agent(self):
        agent = AgentFactory(
            agent_type="langgraph",
            agent_id="TestAgent",
            provider="Ollama",
            model="llama3.2:3b",
        )
        self.assertIsInstance(agent, LangGraphAgent)
        self.assertEqual(agent.agent_id, "TestAgent")

    def test_create_invalid_agent(self):
        with self.assertRaises(ValueError):
            AgentFactory(
                agent_type="unknown",
                agent_id="FakeAgent",
                provider="Ollama",
                model="llama3.2:3b",
            )

if __name__ == "__main__":
    unittest.main()
