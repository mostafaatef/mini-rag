from .BaseLLMProvider import BaseLLMProvider
from ..LLMEnum import OpenAIEnum
from openai import OpenAI
import httpx


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        super().__init__(
            api_key=api_key,
            default_input_max_characters=default_input_max_characters,
            default_generation_max_output_tokens=default_generation_max_output_tokens,
            default_generation_temperature=default_generation_temperature,
        )
        self.base_url = base_url

        http_client = httpx.Client()
        self.client = OpenAI(
            api_key=api_key, base_url=base_url, http_client=http_client
        )
        self.enums = OpenAIEnum

    def generate_response(
        self,
        query: str,
        chat_history: list,
        max_output_tokens: int = None,
        temperature: float = None,
    ) -> str:
        if not self.client:
            self.logger.error("OpenAI client is not initialized")
            return None
        if not self.generation_model_id:
            self.logger.error("OpenAI generation model is not initialized")
            return None

        if not max_output_tokens:
            max_output_tokens = self.default_generation_max_output_tokens
        if not temperature:
            temperature = self.default_generation_temperature

        # Create a new list to avoid side effects on the passed chat_history
        messages = chat_history + [self.construct_prompt(query, OpenAIEnum.USER.value)]

        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=messages,
                max_tokens=max_output_tokens,
                temperature=temperature,
            )
            if (
                not response
                or not response.choices
                or not response.choices[0]
                or not response.choices[0].message
                or not response.choices[0].message.content
            ):
                self.logger.error("OpenAI generation response is empty")
                return None
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return None

    def generate_embedding(self, text: str) -> list:
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else None

    def generate_embeddings(self, texts: list) -> list:
        if not self.client:
            self.logger.error("OpenAI client is not initialized")
            return None
        if not self.embedding_model_id:
            self.logger.error("OpenAI embedding model is not initialized")
            return None
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id, input=texts
            )
            if not response or not response.data:
                self.logger.error("OpenAI embedding response is empty")
                return None
            return [data.embedding for data in response.data]
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
        return None
