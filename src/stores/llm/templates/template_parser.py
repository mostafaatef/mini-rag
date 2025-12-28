import os


class TemplateParser:
    def __init__(self, language: str = None, default_language: str = "en"):
        self.default_language = default_language
        self.base_path = os.path.dirname(__file__)
        self.language = language or default_language

    def get(self, group: str, key: str, variables: dict = None):
        if not group or not key:
            raise ValueError("Group and key are required")

        # Check if localized file exists
        group_file = f"{group}.py"
        lang_path = os.path.join(self.base_path, "locales", self.language, group_file)

        target_lang = self.language
        if not os.path.exists(lang_path):
            # Fallback to default language
            lang_path = os.path.join(
                self.base_path, "locales", self.default_language, group_file
            )
            target_lang = self.default_language

        if not os.path.exists(lang_path):
            return None

        # Dynamic import
        # Assuming src is the root package
        try:
            module_path = f"src.stores.llm.templates.locales.{target_lang}.{group}"
            module = __import__(
                module_path,
                fromlist=[group],
            )
        except ImportError:
            return None

        if not module:
            return None

        template_str = getattr(module, key, None)
        if not template_str:
            return None

        if variables is not None:
            return template_str.substitute(**variables)
        return template_str
