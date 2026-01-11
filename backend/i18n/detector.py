"""
Language Detection Module

Deterministic language detection for English and Spanish text.
Uses pattern-based detection for reliability and testability.
"""

import re
from typing import Tuple
from enum import Enum


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"


class LanguageDetector:
    """
    Deterministic language detector for English and Spanish.

    Detection Strategy:
    1. Check for Spanish-specific characters (ñ, á, é, í, ó, ú, ü, ¿, ¡)
    2. Check for Spanish-specific words (common words that don't exist in English)
    3. Calculate confidence score
    4. Default to English if confidence < 70%
    """

    def __init__(self):
        # Spanish-specific characters (not common in English)
        self.spanish_chars = re.compile(r'[ñáéíóúü¿¡]', re.IGNORECASE)

        # Common Spanish words that are highly indicative
        # These are selected to minimize false positives
        self.spanish_indicators = [
            # Question words
            r'\b(qué|quién|quiénes|cuál|cuáles|cuándo|cuánto|cuánta|cuántos|cuántas|dónde|cómo|por qué)\b',

            # Common verbs
            r'\b(es|son|está|están|hay|tiene|tienen|puede|pueden|quiere|quieren|necesita|necesitan)\b',

            # Articles and pronouns
            r'\b(el|la|los|las|un|una|unos|unas|mi|mis|tu|tus|su|sus|nuestro|nuestra)\b',

            # Prepositions
            r'\b(de|del|para|por|con|sin|sobre|entre|desde|hasta)\b',

            # Common adjectives
            r'\b(bueno|buena|malo|mala|nuevo|nueva|viejo|vieja|grande|pequeño|pequeña)\b',

            # Time/date
            r'\b(hoy|ayer|mañana|ahora|antes|después|siempre|nunca)\b',

            # Common nouns
            r'\b(tienda|producto|cliente|problema|ayuda|información|sistema)\b',
        ]

        # Compile patterns for performance
        self.spanish_pattern = re.compile(
            '|'.join(self.spanish_indicators),
            re.IGNORECASE
        )

        # English-specific common words (for confidence)
        self.english_indicators = [
            r'\b(the|is|are|was|were|have|has|had|will|would|could|should)\b',
            r'\b(what|when|where|why|how|who|which)\b',
            r'\b(this|that|these|those|my|your|our|their)\b',
            r'\b(store|product|customer|problem|help|information|system)\b',
        ]

        self.english_pattern = re.compile(
            '|'.join(self.english_indicators),
            re.IGNORECASE
        )

    def detect(self, text: str) -> Tuple[Language, float]:
        """
        Detect language of input text.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (Language enum, confidence score 0.0-1.0)

        Algorithm:
        1. Check for Spanish-specific characters (high confidence)
        2. Count Spanish indicator words
        3. Count English indicator words
        4. Calculate confidence based on ratios
        5. Default to English if confidence < 0.7
        """
        if not text or not text.strip():
            return Language.ENGLISH, 1.0

        text = text.lower().strip()

        # Quick check: Spanish-specific characters
        spanish_chars_count = len(self.spanish_chars.findall(text))

        # Count indicator words
        spanish_matches = len(self.spanish_pattern.findall(text))
        english_matches = len(self.english_pattern.findall(text))

        # Calculate total words for normalization
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)

        if total_words == 0:
            return Language.ENGLISH, 1.0

        # Scoring algorithm
        spanish_score = 0.0
        english_score = 0.0

        # Spanish character presence is strong indicator
        if spanish_chars_count > 0:
            spanish_score += min(spanish_chars_count * 0.3, 0.5)

        # Word-based scoring (normalized by text length)
        if total_words > 0:
            spanish_score += (spanish_matches / total_words) * 0.5
            english_score += (english_matches / total_words) * 0.5

        # Determine language
        if spanish_score > english_score and spanish_score >= 0.3:
            confidence = min(spanish_score, 1.0)
            return Language.SPANISH, confidence
        else:
            confidence = max(english_score, 0.7)  # Default to high confidence for English
            return Language.ENGLISH, min(confidence, 1.0)

    def detect_language_code(self, text: str) -> str:
        """
        Convenience method that returns language code as string.

        Args:
            text: Input text

        Returns:
            Language code: "en" or "es"
        """
        language, _ = self.detect(text)
        return language.value

    def detect_with_metadata(self, text: str) -> dict:
        """
        Detect language with full metadata for logging.

        Args:
            text: Input text

        Returns:
            Dictionary with language, confidence, and detection details
        """
        language, confidence = self.detect(text)

        return {
            "language": language.value,
            "language_name": "English" if language == Language.ENGLISH else "Spanish",
            "confidence": round(confidence, 2),
            "text_length": len(text),
            "detection_method": "pattern_based"
        }


# Global detector instance
detector = LanguageDetector()


def detect_language(text: str) -> str:
    """
    Module-level convenience function for language detection.

    Args:
        text: Input text

    Returns:
        Language code: "en" or "es"
    """
    return detector.detect_language_code(text)
