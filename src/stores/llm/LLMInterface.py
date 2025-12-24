from abc import ABC, abstractmethod


class LLMInterface(ABC):
    @abstractmethod
    def set_generation_model(self, model_name: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_name: str, embedding_model_size: int):
        pass

    @abstractmethod
    def generate_response(
        self,
        query: str,
        chat_history: list,
        max_output_tokens: int,
        temperature: float = None,
    ):
        pass

    @abstractmethod
    def generate_embedding(self, text: str, input_type: str = None):
        pass

    @abstractmethod
    def construct_prompt(self, query: str, role: str):
        pass
