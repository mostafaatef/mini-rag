from ..LLMInterface import LLMInterface
from logging import getLogger


class BaseLLMProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_model_size = None

        self.logger = getLogger(__name__)

    def set_generation_model(self, model_name: str):
        self.generation_model_id = model_name

    def set_embedding_model(self, model_name: str, embedding_model_size: int):
        self.embedding_model_id = model_name
        self.embedding_model_size = embedding_model_size

    def process_input(self, text: str) -> str:
        return text[: self.default_input_max_characters].strip()

    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {"role": role, "content": self.process_input(prompt)}
