"""
Unit Tests for Language Detector

Tests deterministic language detection for English and Spanish.
"""

import pytest
from backend.i18n.detector import LanguageDetector, Language


class TestLanguageDetector:
    """Test suite for LanguageDetector"""

    @pytest.fixture
    def detector(self):
        """Fixture providing LanguageDetector instance"""
        return LanguageDetector()

    # English Detection Tests

    def test_english_simple_question(self, detector):
        """Test English detection: simple question"""
        text = "What is the store policy on returns?"
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH
        assert confidence >= 0.7

    def test_english_technical_query(self, detector):
        """Test English detection: technical query"""
        text = "How do I reset the kiosk system when it shows an error?"
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH
        assert confidence >= 0.7

    def test_english_with_numbers(self, detector):
        """Test English detection: text with numbers"""
        text = "The POS system in store 1234 has 3 terminals down"
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH
        assert confidence >= 0.7

    # Spanish Detection Tests

    def test_spanish_simple_question(self, detector):
        """Test Spanish detection: simple question"""
        text = "¿Cuál es la política de la tienda sobre devoluciones?"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH
        assert confidence >= 0.3

    def test_spanish_technical_query(self, detector):
        """Test Spanish detection: technical query"""
        text = "¿Cómo reinicio el sistema del quiosco cuando muestra un error?"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH
        assert confidence >= 0.3

    def test_spanish_without_accents(self, detector):
        """Test Spanish detection: without accent marks"""
        text = "Donde esta el inventario de la tienda?"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH
        assert confidence >= 0.3

    def test_spanish_with_tildes(self, detector):
        """Test Spanish detection: with ñ character"""
        text = "El niño necesita ayuda con el producto mañana"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH
        # High confidence due to ñ
        assert confidence >= 0.5

    def test_spanish_common_words(self, detector):
        """Test Spanish detection: common Spanish words"""
        text = "La tienda tiene productos nuevos hoy"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH
        assert confidence >= 0.3

    # Edge Cases

    def test_empty_string(self, detector):
        """Test detection: empty string defaults to English"""
        text = ""
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH
        assert confidence == 1.0

    def test_whitespace_only(self, detector):
        """Test detection: whitespace only defaults to English"""
        text = "   \n\t   "
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH
        assert confidence == 1.0

    def test_numbers_only(self, detector):
        """Test detection: numbers only defaults to English"""
        text = "12345 67890"
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH

    def test_mixed_language_english_dominant(self, detector):
        """Test detection: mixed language (English dominant)"""
        text = "The store tiene new products hoy"
        lang, confidence = detector.detect(text)

        # Should detect as English due to more English indicators
        assert lang == Language.ENGLISH

    def test_mixed_language_spanish_dominant(self, detector):
        """Test detection: mixed language (Spanish dominant)"""
        text = "La tienda has new productos today"
        lang, confidence = detector.detect(text)

        # Should detect as Spanish due to more Spanish indicators
        assert lang == Language.SPANISH

    # Convenience Methods

    def test_detect_language_code_english(self, detector):
        """Test detect_language_code: returns 'en'"""
        text = "How are you today?"
        code = detector.detect_language_code(text)

        assert code == "en"

    def test_detect_language_code_spanish(self, detector):
        """Test detect_language_code: returns 'es'"""
        text = "¿Cómo estás hoy?"
        code = detector.detect_language_code(text)

        assert code == "es"

    def test_detect_with_metadata(self, detector):
        """Test detect_with_metadata: returns full metadata"""
        text = "¿Qué hora es?"
        metadata = detector.detect_with_metadata(text)

        assert "language" in metadata
        assert "language_name" in metadata
        assert "confidence" in metadata
        assert "text_length" in metadata
        assert "detection_method" in metadata

        assert metadata["language"] == "es"
        assert metadata["language_name"] == "Spanish"
        assert metadata["text_length"] == len(text)
        assert metadata["detection_method"] == "pattern_based"

    # Real-World Scenarios

    def test_retail_english_query(self, detector):
        """Test detection: real retail query in English"""
        text = "Why is the kiosk showing incorrect store information?"
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH
        assert confidence >= 0.7

    def test_retail_spanish_query(self, detector):
        """Test detection: real retail query in Spanish"""
        text = "¿Por qué el quiosco muestra información incorrecta de la tienda?"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH
        assert confidence >= 0.3

    def test_inventory_english(self, detector):
        """Test detection: inventory question in English"""
        text = "What is the current stock level for item SKU-12345?"
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH

    def test_inventory_spanish(self, detector):
        """Test detection: inventory question in Spanish"""
        text = "¿Cuál es el nivel de inventario actual para el artículo SKU-12345?"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH

    def test_policy_english(self, detector):
        """Test detection: policy question in English"""
        text = "What are the holiday return policies for electronics?"
        lang, confidence = detector.detect(text)

        assert lang == Language.ENGLISH

    def test_policy_spanish(self, detector):
        """Test detection: policy question in Spanish"""
        text = "¿Cuáles son las políticas de devolución navideñas para electrónicos?"
        lang, confidence = detector.detect(text)

        assert lang == Language.SPANISH

    # Case Sensitivity

    def test_case_insensitive_english(self, detector):
        """Test detection: case insensitive for English"""
        text_lower = "what is the store policy?"
        text_upper = "WHAT IS THE STORE POLICY?"
        text_mixed = "WhAt Is ThE sToRe PoLiCy?"

        lang_lower, _ = detector.detect(text_lower)
        lang_upper, _ = detector.detect(text_upper)
        lang_mixed, _ = detector.detect(text_mixed)

        assert lang_lower == Language.ENGLISH
        assert lang_upper == Language.ENGLISH
        assert lang_mixed == Language.ENGLISH

    def test_case_insensitive_spanish(self, detector):
        """Test detection: case insensitive for Spanish"""
        text_lower = "¿cuál es la política de la tienda?"
        text_upper = "¿CUÁL ES LA POLÍTICA DE LA TIENDA?"
        text_mixed = "¿CuÁl Es La PoLíTiCa De La TiEnDa?"

        lang_lower, _ = detector.detect(text_lower)
        lang_upper, _ = detector.detect(text_upper)
        lang_mixed, _ = detector.detect(text_mixed)

        assert lang_lower == Language.SPANISH
        assert lang_upper == Language.SPANISH
        assert lang_mixed == Language.SPANISH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
