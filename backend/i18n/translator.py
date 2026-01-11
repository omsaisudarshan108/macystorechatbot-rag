"""
Translation Service

Provides translation utilities for English and Spanish.
Loads translations from JSON files and supports variable interpolation.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


class TranslationService:
    """
    Translation service for loading and managing translations.

    Supports:
    - Loading translations from JSON files
    - Variable interpolation ({{variable}})
    - Nested key access (dot notation)
    - Fallback to English for missing translations
    """

    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_translations()

    def load_translations(self):
        """Load translation files from translations directory"""
        translations_dir = Path(__file__).parent / "translations"

        # Load English
        en_file = translations_dir / "en.json"
        if en_file.exists():
            with open(en_file, 'r', encoding='utf-8') as f:
                self.translations['en'] = json.load(f)

        # Load Spanish
        es_file = translations_dir / "es.json"
        if es_file.exists():
            with open(es_file, 'r', encoding='utf-8') as f:
                self.translations['es'] = json.load(f)

    def get(self, key: str, language: str = 'en', **variables) -> str:
        """
        Get translated text for a given key.

        Args:
            key: Translation key (dot notation, e.g., "app.title")
            language: Language code ("en" or "es")
            **variables: Variables for interpolation

        Returns:
            Translated text with variables interpolated

        Example:
            translator.get("errors.generic", language="es", error="Connection failed")
        """
        # Normalize language code
        language = self._normalize_language(language)

        # Get translation from specified language
        text = self._get_nested_key(key, language)

        # Fallback to English if not found
        if text is None and language != 'en':
            text = self._get_nested_key(key, 'en')

        # If still not found, return key
        if text is None:
            return key

        # Interpolate variables
        if variables:
            text = self._interpolate(text, variables)

        return text

    def _normalize_language(self, language: str) -> str:
        """Normalize language code to 'en' or 'es'"""
        language = language.lower().strip()

        # Handle variations
        if language in ['en', 'eng', 'english', 'en-us', 'en-gb']:
            return 'en'
        elif language in ['es', 'esp', 'spanish', 'es-es', 'es-mx', 'español']:
            return 'es'

        # Default to English
        return 'en'

    def _get_nested_key(self, key: str, language: str) -> Optional[str]:
        """
        Get value from nested dictionary using dot notation.

        Args:
            key: Dot-separated key path (e.g., "app.title")
            language: Language code

        Returns:
            Translation string or None if not found
        """
        if language not in self.translations:
            return None

        keys = key.split('.')
        value = self.translations[language]

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value if isinstance(value, str) else None

    def _interpolate(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Interpolate variables into text.

        Supports {{variable}} syntax.

        Args:
            text: Text with variable placeholders
            variables: Dictionary of variable values

        Returns:
            Text with variables replaced
        """
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r'\{\{(\w+)\}\}', replace_var, text)

    def get_all(self, language: str = 'en') -> Dict[str, Any]:
        """
        Get all translations for a language.

        Args:
            language: Language code

        Returns:
            Dictionary of all translations
        """
        language = self._normalize_language(language)
        return self.translations.get(language, self.translations.get('en', {}))

    def get_language_name(self, language_code: str) -> str:
        """
        Get human-readable language name.

        Args:
            language_code: Language code ("en" or "es")

        Returns:
            Language name
        """
        language_code = self._normalize_language(language_code)

        names = {
            'en': 'English',
            'es': 'Español'
        }

        return names.get(language_code, 'English')


# Global translator instance
translator = TranslationService()


def translate(key: str, language: str = 'en', **variables) -> str:
    """
    Module-level convenience function for translation.

    Args:
        key: Translation key
        language: Language code
        **variables: Variables for interpolation

    Returns:
        Translated text
    """
    return translator.get(key, language, **variables)


def get_translations(language: str = 'en') -> Dict[str, Any]:
    """
    Module-level convenience function to get all translations.

    Args:
        language: Language code

    Returns:
        Dictionary of all translations
    """
    return translator.get_all(language)
