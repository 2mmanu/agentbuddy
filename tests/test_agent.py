import unittest
from agentbuddy.agents.langgraph_agent import LangGraphAgent
from langchain_ollama import ChatOllama

def search(query: str):
    """Call to surf the web."""
    # This is a placeholder, but don't tell the LLM that...
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 70 degrees and foggy."
    return "It's 90 degrees and sunny."

class TestLangGraphAgent(unittest.TestCase):

    def setUp(self):
        """Set up the agent for testing."""
        llm = ChatOllama(model="llama3.2:3b")
        self.agent = LangGraphAgent("agent_id", tools=[search], llm=llm)

    def test_weather_in_sf(self):
        """Test the response when asking about the weather in San Francisco."""
        query = "what is the weather in san francisco"
        resp = self.agent.interact(query)
        self.assertIn("70", resp[-1].content)

    def test_weather_in_other_location(self):
        """Test the response when asking about the weather in another location."""
        query = "what is the weather in miami"
        resp = self.agent.interact(query)
        self.assertIn("90", resp[-1].content)

if __name__ == "__main__":
    unittest.main()