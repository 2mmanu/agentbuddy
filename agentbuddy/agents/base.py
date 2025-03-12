from abc import ABC, abstractmethod

class AgentBase(ABC):
    @abstractmethod
    def __init__(self, agent_id, tools=None, **kwargs):
        """
        Inizializza l'agente.
        """
        self.agent_id = agent_id
        self.tools = tools if tools else []
        self.model = kwargs.get('model', 'llama3.2:3b')

    @abstractmethod
    def create_base_agent(self):
        """
        Crea un agente base, da implementare nelle classi derivate.
        """
        pass

    @abstractmethod
    def interact(self, input_text):
        """
        Simula l'interazione con l'agente.
        """
        pass