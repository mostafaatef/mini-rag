from .BaseLLMProvider import BaseLLMProvider
from ..LLMEnum import CohereEnum, InputType

try:
    import cohere
except ImportError:
    cohere = None


class CohereProvider(BaseLLMProvider):
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

        if cohere:
            self.client = cohere.Client(
                api_key=api_key,
            )
        else:
            self.client = None
            self.logger.warning("Cohere library not found. CohereProvider disabled.")

        self.enums = CohereEnum

    def generate_response(
        self,
        query: str,
        chat_history: list,
        max_output_tokens: int = None,
        temperature: float = None,
    ):
        if not self.client:
            self.logger.error("Cohere client is not initialized")
            return None
        if not self.generation_model_id:
            self.logger.error("Cohere generation model is not initialized")
            return None

        if not max_output_tokens:
            max_output_tokens = self.default_generation_max_output_tokens
        if not temperature:
            temperature = self.default_generation_temperature

        # Cohere API uses 'chat_history' + 'message' parameter
        # OpenAI uses a list of messages. We need to adapt.
        # Assuming chat_history passed here is a list of dicts {"role": ..., "content": ...} like OpenAIProvider

        # Helper to convert internal role enum to Cohere roles if needed,
        # but usually Cohere uses USER/CHATBOT in chat_history.

        # Current implementation of generate_response in OpenAI provider appends the current query to chat_history
        # and sends the whole list.
        # Cohere's client.chat expects `message` (current query) and `chat_history` (previous turns).

        current_message = self.process_input(query)

        # We need to separate the history from the current message if possible,
        # OR just format everything as a prompt if using a distinct API.
        # However, assuming we want to use the Chat endpoint:

        provider_chat_history = []
        preamble = None
        for msg in chat_history:
            role = msg.get("role")
            content = msg.get("content")
            if role == CohereEnum.USER.value:
                provider_chat_history.append({"role": "USER", "message": content})
            elif role == CohereEnum.CHATBOT.value:
                provider_chat_history.append({"role": "CHATBOT", "message": content})
            elif role == CohereEnum.SYSTEM.value:
                preamble = content

        try:
            response = self.client.chat(
                model=self.generation_model_id,
                message=current_message,
                chat_history=provider_chat_history,
                preamble=preamble,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )

            if not response or not response.text:
                self.logger.error("Cohere generation response is empty")
                return None

            return response.text

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return None

    def generate_embedding(self, text: str, input_type: str = None) -> list:
        if not self.client:
            self.logger.error("Cohere client is not initialized")
            return None
        if not self.embedding_model_id:
            self.logger.error("Cohere embedding model is not initialized")
            return None
        try:
            search_input_type = CohereEnum.DOCUMENT_INPUT_TYPE.value
            if input_type == InputType.QUERY.value:
                search_input_type = CohereEnum.QUERY_INPUT_TYPE.value

            response = self.client.embed(
                model=self.embedding_model_id,
                texts=[self.process_input(text)],
                input_type=search_input_type,
                embedding_types=["float"],
            )
            if (
                not response
                or not response.embeddings
                or not response.embeddings.float
                or not response.embeddings.float[0]
            ):
                self.logger.error("Cohere embedding response is empty")
                return None
            return response.embeddings.float[0]
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
        return None
