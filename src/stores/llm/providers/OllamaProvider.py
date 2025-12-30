from .BaseLLMProvider import BaseLLMProvider
from ..LLMEnum import OpenAIEnum
from openai import OpenAI
import httpx


class OllamaProvider(BaseLLMProvider):
    def __init__(
        self,
        base_url: str,
        api_key: str = "ollama",  # Ollama doesn't require an API key usually
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
            self.logger.error("Ollama client is not initialized")
            return None
        if not self.generation_model_id:
            self.logger.error("Ollama generation model is not initialized")
            return None

        if not max_output_tokens:
            max_output_tokens = self.default_generation_max_output_tokens
        if not temperature:
            temperature = self.default_generation_temperature

        # Create a new list to avoid side effects on the passed chat_history
        messages = chat_history + [self.construct_prompt(query, OpenAIEnum.USER.value)]

        try:
            # Note: Ollama might handle max_tokens differently or ignore it depending on version,
            # but standard OpenAI client sends it.
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
                self.logger.error("Ollama generation response is empty")
                return None
            content = response.choices[0].message.content
            # Check if the model echoed the prompt (common with some Ollama models/configs)
            last_message_content = messages[-1]["content"] if messages else ""
            if (
                content
                and last_message_content
                and content.strip().startswith(last_message_content.strip()[:50])
            ):  # Check first 50 chars to avoid full strings comparison issues
                # Logic: If content starts with the prompt, likely it echoed.
                # However, exact match might fail due to whitespace.
                # Let's try to remove the prompt part if it seems to be a prefix.
                if content.strip().startswith(last_message_content.strip()):
                    content = content.strip()[
                        len(last_message_content.strip()) :
                    ].strip()

            return content
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return None

    def generate_embedding(self, text: str, input_type: str = None) -> list:
        embeddings = self.generate_embeddings([text], input_type)
        return embeddings[0] if embeddings else None

    def generate_embeddings(self, texts: list, input_type: str = None) -> list:
        if not self.client:
            self.logger.error("Ollama client is not initialized")
            return None
        if not self.embedding_model_id:
            self.logger.error("Ollama embedding model is not initialized")
            return None
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id, input=texts
            )
            if not response or not response.data:
                self.logger.error("Ollama embedding response is empty")
                return None
            return [data.embedding for data in response.data]
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
        return None
