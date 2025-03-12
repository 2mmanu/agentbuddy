from abc import ABC, abstractmethod

class AgentBase(ABC):
    @abstractmethod
    def __init__(self, agent_id, tools=None, **kwargs):
        """
        Inizializza l'agente.
        - `llm`: Un'istanza di una classe LLM personalizzata (opzionale).
        - `provider`: Il provider di LLM (es. 'Ollama', 'Azure').
        - `model`: Il modello da usare con il provider specificato.
        """
        self.agent_id = agent_id
        self.tools = tools if tools else []
        
        if 'llm' in kwargs:
            self.llm = kwargs['llm']
        else:
            self.provider = kwargs.get('provider')
            self.model = kwargs.get('model')

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