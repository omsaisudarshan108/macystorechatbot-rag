"""
Internationalization Module

Provides language detection and translation services for English and Spanish.
"""

from .detector import LanguageDetector
from .translator import TranslationService

__all__ = ['LanguageDetector', 'TranslationService']
