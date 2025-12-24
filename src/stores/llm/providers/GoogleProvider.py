from .BaseLLMProvider import BaseLLMProvider
from ..LLMEnum import GoogleEnum, InputType

try:
    import google.generativeai as genai
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
            genai.configure(api_key=self.api_key)
        else:
            self.logger.warning(
                "Google Generative AI library not found. GoogleProvider disabled."
            )

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

        if not max_output_tokens:
            max_output_tokens = self.default_generation_max_output_tokens
        if not temperature:
            temperature = self.default_generation_temperature

        # Prepare history for Gemini
        # Gemini expects history as a list of contents: [{"role": "user", "parts": ["text"]}, ...]
        # We assume chat_history comes in as a list of dicts: {"role": ..., "content": ...}

        gemini_history = []
        for msg in chat_history:
            role = msg.get("role")
            content = msg.get("content")

            if role == GoogleEnum.USER.value:
                gemini_history.append({"role": "user", "parts": [content]})
            elif role == GoogleEnum.MODEL.value:
                gemini_history.append({"role": "model", "parts": [content]})
            # Ignore system messages or others as Gemini Chat mainly supports user/model turns strictly in some versions

        # Configure the model
        model = genai.GenerativeModel(self.generation_model_id)

        try:
            # Start chat session
            chat = model.start_chat(history=gemini_history)

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_output_tokens, temperature=temperature
            )

            response = chat.send_message(
                self.process_input(query), generation_config=generation_config
            )

            if not response or not response.text:
                self.logger.error("Google generation response is empty")
                return None

            return response.text

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return None

    def generate_embedding(self, text: str, input_type: str = None) -> list:
        if not self.embedding_model_id:
            self.logger.error("Google embedding model is not initialized")
            return None
        try:
            result = genai.embed_content(
                model=self.embedding_model_id,
                content=text,
                task_type=GoogleEnum.DOCUMENT_INPUT_TYPE.value
                if input_type == InputType.DOCUMENT.value
                else GoogleEnum.QUERY_INPUT_TYPE.value,
                title=None,  # Title is optional/needed for retrieval_document in some cases but generic here
            )

            if not result or "embedding" not in result:
                self.logger.error("Google embedding response is empty")
                return None

            return result["embedding"]
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
        return None
