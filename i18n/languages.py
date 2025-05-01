from i18n.languages_dict.french import *
from i18n.languages_dict.english import *
from config.settings import DEFAULT_LANGUAGE

class LanguageConfig:

    def __init__(self):
        self.language_strings = {
            "FR": french,
            "EN": english
        }
        self.selected_language = self.language_strings[DEFAULT_LANGUAGE]  # Default dictionary

    def set_language(self, language_code):
        """Define the selected language"""
        language_code = language_code.upper()
        self.selected_language = self.language_strings.get(language_code, self.language_strings["EN"])
        return self.selected_language

    def get_string(self, key, **kwargs):
        """Retrieves a translated string with variable interpolation"""
        if key not in self.selected_language:
            return f"[MISSING: {key}]"

        # Variable interpolation in the translated string
        return self.selected_language[key].format(**kwargs) if kwargs else self.selected_language[key]


language_config = LanguageConfig()  # Global instance