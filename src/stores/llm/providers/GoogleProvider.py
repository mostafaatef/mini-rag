from .BaseLLMProvider import BaseLLMProvider
from ..LLMEnum import GoogleEnum, InputType

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


class GoogleProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
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

        if genai:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            self.logger.warning(
                "Google GenAI library not found. GoogleProvider disabled."
            )
        self.enums = GoogleEnum

    def generate_response(
        self,
        query: str,
        chat_history: list,
        max_output_tokens: int = None,
        temperature: float = None,
    ) -> str:
        if not self.generation_model_id:
            self.logger.error("Google generation model is not initialized")
            return None

        if not self.client:
            self.logger.error("Google GenAI client is not initialized")
            return None

        if not max_output_tokens:
            max_output_tokens = self.default_generation_max_output_tokens
        if not temperature:
            temperature = self.default_generation_temperature

        # Prepare history for Gemini
        # New SDK supports standard message format but let's stick to simple Content objects or equivalent
        # For simplicity, we can pass chat history but the new generate_content is stateless unless using chats.
        # Let's assume stateless generate_content with history passed as 'contents' if possible,
        # or just prompt + query.

        # However, new SDK `chats.create` is good for history.
        # Let's try to adapt the history format.

        contents = []
        system_instruction = None

        for msg in chat_history:
            role = msg.get("role")
            content = msg.get("content")
            if role == GoogleEnum.USER.value:
                contents.append(
                    types.Content(role="user", parts=[types.Part(text=content)])
                )
            elif role == GoogleEnum.MODEL.value:
                contents.append(
                    types.Content(role="model", parts=[types.Part(text=content)])
                )
            elif role == GoogleEnum.SYSTEM.value:
                system_instruction = content

        # Add current query
        contents.append(
            types.Content(
                role="user", parts=[types.Part(text=self.process_input(query))]
            )
        )

        import time

        retries = 5
        base_delay = 2

        for attempt in range(retries):
            try:
                config = types.GenerateContentConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    system_instruction=system_instruction,
                )

                # Using models.generate_content for simpler stateless call with full history context
                response = self.client.models.generate_content(
                    model=self.generation_model_id, contents=contents, config=config
                )

                if not response or not response.text:
                    self.logger.error("Google generation response is empty")
                    with open("/tmp/google_provider_error.log", "w") as f:
                        f.write(
                            f"Error: Google generation response is empty. Response object: {response}\n"
                        )
                    return None

                return response.text

            except Exception as e:
                error_str = str(e)
                if (
                    "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
                ) and attempt < retries - 1:
                    sleep_time = base_delay * (2**attempt)
                    self.logger.warning(
                        f"Google Rate Limit Hit. Retrying in {sleep_time}s... (Attempt {attempt + 1}/{retries})"
                    )
                    time.sleep(sleep_time)
                    continue

                self.logger.error(f"Error generating response: {error_str}")
                return None

    def generate_embedding(self, text: str, input_type: str = None) -> list:
        embeddings = self.generate_embeddings([text], input_type)
        return embeddings[0] if embeddings else None

    def generate_embeddings(self, texts: list, input_type: str = None) -> list:
        if not self.embedding_model_id:
            self.logger.error("Google embedding model is not initialized")
            return None

        if not self.client:
            self.logger.error("Google GenAI client is not initialized")
            return None

        task_type = (
            "RETRIEVAL_DOCUMENT"
            if input_type == InputType.DOCUMENT.value
            else "RETRIEVAL_QUERY"
        )

        try:
            # New SDK supports list of strings in contents
            result = self.client.models.embed_content(
                model=self.embedding_model_id,
                contents=texts,
                config=types.EmbedContentConfig(task_type=task_type, title=None),
            )

            if not result or not result.embeddings:
                self.logger.error("Google embedding response is empty")
                return None

            return [emb.values for emb in result.embeddings]

        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
        return None
