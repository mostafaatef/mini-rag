from .providers import OpenAIProvider, CohereProvider, GoogleProvider, OllamaProvider
from .LLMEnum import LLMEnum


class LLMProviderFactory:
    def __init__(self, settings):
        self.settings = settings

    def create_provider(self, provider_name: str):
        if provider_name == LLMEnum.OPENAI.value:
            return OpenAIProvider(
                api_key=self.settings.OPENAI_API_KEY,
                base_url=self.settings.OPENAI_API_URL,
                default_input_max_characters=self.settings.INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.settings.GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.settings.GENERATION_TEMPERATURE,
            )
        elif provider_name == LLMEnum.COHERE.value:
            return CohereProvider(
                api_key=self.settings.COHERE_API_KEY,
                default_input_max_characters=self.settings.INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.settings.GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.settings.GENERATION_TEMPERATURE,
            )
        elif provider_name == LLMEnum.GOOGLE.value:
            return GoogleProvider(
                api_key=self.settings.GOOGLE_API_KEY,
                default_input_max_characters=self.settings.INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.settings.GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.settings.GENERATION_TEMPERATURE,
            )
        elif provider_name == LLMEnum.OLLAMA.value:
            return OllamaProvider(
                base_url=self.settings.OLLAMA_BASE_URL,
                default_input_max_characters=self.settings.INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.settings.GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.settings.GENERATION_TEMPERATURE,
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
