"""
Frontend i18n Utilities

Provides translation functions for Streamlit UI with full WCAG 2.1 AA compliance.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import re


class UITranslator:
    """
    UI translation service for Streamlit frontend.

    Loads translations from backend i18n files and provides
    utility functions for component localization.
    """

    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_translations()

    def load_translations(self):
        """Load translations from backend i18n directory"""
        # Path to backend translations
        backend_i18n = Path(__file__).parent.parent / "backend" / "i18n" / "translations"

        # Load English
        en_file = backend_i18n / "en.json"
        if en_file.exists():
            with open(en_file, 'r', encoding='utf-8') as f:
                self.translations['en'] = json.load(f)

        # Load Spanish
        es_file = backend_i18n / "es.json"
        if es_file.exists():
            with open(es_file, 'r', encoding='utf-8') as f:
                self.translations['es'] = json.load(f)

    def t(self, key: str, lang: str = 'en', **variables) -> str:
        """
        Translate a key to specified language.

        Args:
            key: Translation key (dot notation)
            lang: Language code ('en' or 'es')
            **variables: Variables for interpolation

        Returns:
            Translated text
        """
        lang = self._normalize_lang(lang)

        # Get translation
        text = self._get_nested(key, lang)

        # Fallback to English
        if text is None and lang != 'en':
            text = self._get_nested(key, 'en')

        # Return key if not found
        if text is None:
            return key

        # Interpolate variables
        if variables:
            text = self._interpolate(text, variables)

        return text

    def _normalize_lang(self, lang: str) -> str:
        """Normalize language code"""
        lang = lang.lower().strip()
        if lang in ['es', 'spanish', 'español']:
            return 'es'
        return 'en'

    def _get_nested(self, key: str, lang: str) -> Optional[str]:
        """Get nested value from translation dict"""
        if lang not in self.translations:
            return None

        keys = key.split('.')
        value = self.translations[lang]

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value if isinstance(value, str) else None

    def _interpolate(self, text: str, variables: Dict[str, Any]) -> str:
        """Interpolate variables into text"""
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r'\{\{(\w+)\}\}', replace_var, text)

    def get_lang_attr(self, lang: str) -> str:
        """Get HTML lang attribute value"""
        return 'es' if lang == 'es' else 'en'

    def get_lang_name(self, lang: str) -> str:
        """Get human-readable language name"""
        return 'Español' if lang == 'es' else 'English'


# Global translator instance
ui_translator = UITranslator()


def translate(key: str, lang: str = 'en', **variables) -> str:
    """
    Module-level translation function.

    Args:
        key: Translation key
        lang: Language code
        **variables: Variables for interpolation

    Returns:
        Translated text
    """
    return ui_translator.t(key, lang, **variables)


def get_language_from_response(response: dict) -> str:
    """
    Extract language from API response.

    Args:
        response: API response dictionary

    Returns:
        Language code ('en' or 'es')
    """
    return response.get('language', 'en')


def create_lang_div(content: str, lang: str, role: Optional[str] = None,
                    aria_live: Optional[str] = None, aria_label: Optional[str] = None) -> str:
    """
    Create a div with proper lang attribute and ARIA attributes.

    Args:
        content: HTML content
        lang: Language code
        role: ARIA role
        aria_live: ARIA live region type
        aria_label: ARIA label

    Returns:
        HTML div with accessibility attributes
    """
    lang_attr = ui_translator.get_lang_attr(lang)

    attrs = [f'lang="{lang_attr}"']

    if role:
        attrs.append(f'role="{role}"')

    if aria_live:
        attrs.append(f'aria-live="{aria_live}"')

    if aria_label:
        attrs.append(f'aria-label="{aria_label}"')

    attrs_str = ' '.join(attrs)

    return f'<div {attrs_str}>{content}</div>'
