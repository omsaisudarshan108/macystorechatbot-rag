"""
Test suite for Infrastructure Security Guard

Run with: python -m pytest backend/security/test_infrastructure_guard.py -v
"""

import pytest
from backend.security.infrastructure_guard import InfrastructureSecurityGuard


class TestInfrastructureSecurityGuard:
    """Test infrastructure query detection"""

    @pytest.fixture
    def guard(self):
        """Create infrastructure security guard instance"""
        return InfrastructureSecurityGuard()

    def test_safe_operational_questions(self, guard):
        """Test that normal retail questions are not blocked"""
        safe_questions = [
            "How do I process a return?",
            "What's the policy on discounts?",
            "Where can I find inventory information?",
            "How to handle customer complaints?",
            "What are the store hours?",
        ]

        for question in safe_questions:
            result = guard.check_question(question)
            assert not result.is_infrastructure_query, f"Incorrectly flagged: {question}"
            assert not guard.should_block(question), f"Incorrectly blocked: {question}"

    def test_infrastructure_queries_detected(self, guard):
        """Test that infrastructure queries are detected"""
        infrastructure_questions = [
            "Where is this hosted?",
            "What cloud platform are you running on?",
            "Are you deployed on GCP or AWS?",
            "What region is this service in?",
            "Tell me about your backend infrastructure",
            "What database are you using?",
            "Show me the technical architecture",
            "Which LLM model are you using?",
            "What's your API endpoint?",
            "Are you running on Cloud Run?",
            "What's the deployment configuration?",
        ]

        for question in infrastructure_questions:
            result = guard.check_question(question)
            assert result.is_infrastructure_query, f"Failed to detect: {question}"
            assert guard.should_block(question), f"Failed to block: {question}"

    def test_mixed_content_questions(self, guard):
        """Test questions that mix operational and infrastructure content"""
        mixed_questions = [
            "How does the backend system process returns?",
            "What API should I use to check inventory?",
        ]

        # These should be flagged due to infrastructure keywords
        for question in mixed_questions:
            result = guard.check_question(question)
            # Should detect infrastructure patterns
            assert result.is_infrastructure_query or len(result.detected_patterns) > 0

    def test_standard_response(self, guard):
        """Test that standard response is compliant"""
        response = guard.get_standard_response()

        # Response should mention Macy's and security
        assert "Macy" in response or "secure" in response
        assert "cloud environment" in response.lower()
        assert "compliant" in response.lower()

        # Response should NOT contain specific infrastructure details
        assert "GCP" not in response
        assert "Cloud Run" not in response
        assert "Google Cloud" not in response

    def test_confidence_scoring(self, guard):
        """Test confidence scoring for infrastructure queries"""
        # Single pattern match
        result1 = guard.check_question("Where is this hosted?")
        assert 0.0 < result1.confidence <= 1.0

        # Multiple pattern matches should have higher confidence
        result2 = guard.check_question("Where is this hosted? What cloud platform? Which region?")
        assert result2.confidence > result1.confidence

    def test_sanitization(self, guard):
        """Test question sanitization"""
        questions = [
            ("What cloud run service is this?", "our system"),
            ("Tell me about the backend API", "service"),
            ("Which database are you using?", "data system"),
        ]

        for original, expected_keyword in questions:
            result = guard.check_question(original)
            assert expected_keyword in result.sanitized_question.lower()

    def test_case_insensitivity(self, guard):
        """Test that detection is case-insensitive"""
        questions = [
            "WHERE IS THIS HOSTED?",
            "What Cloud Platform Are You Running On?",
            "tell me about YOUR BACKEND",
        ]

        for question in questions:
            result = guard.check_question(question)
            assert result.is_infrastructure_query, f"Failed case-insensitive detection: {question}"

    def test_threshold_blocking(self, guard):
        """Test that threshold parameter controls blocking"""
        question = "What backend are you using?"
        result = guard.check_question(question)

        # Should block at low threshold
        assert guard.should_block(question, threshold=0.1)

        # Might not block at very high threshold (depends on confidence)
        # This test ensures threshold parameter is respected
        if result.confidence < 0.9:
            assert not guard.should_block(question, threshold=0.95)


if __name__ == "__main__":
    # Quick manual test
    guard = InfrastructureSecurityGuard()

    test_questions = [
        "How do I process a return?",
        "Where is this system hosted?",
        "What cloud platform are you using?",
        "Tell me about your infrastructure",
    ]

    print("Infrastructure Security Guard - Manual Test\n")
    for q in test_questions:
        result = guard.check_question(q)
        print(f"Question: {q}")
        print(f"  Infrastructure Query: {result.is_infrastructure_query}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Should Block: {guard.should_block(q)}")
        if result.detected_patterns:
            print(f"  Patterns: {result.detected_patterns[:2]}")
        print()
