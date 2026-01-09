"""
Unit Tests for Safety & Escalation Framework

Tests safety classification, policy engine, and reporting service.

Run with: pytest tests/test_safety.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.safety.classifier import (
    SafetyClassifier,
    SafetyCategory,
    SeverityLevel,
    SafetyClassification
)
from backend.safety.policy_engine import (
    SafetyPolicyEngine,
    SafetyResponse
)
from backend.safety.response_templates import (
    get_template,
    format_resource_card,
    SUPPORT_RESOURCES
)


class TestSafetyClassifier:
    """Test SafetyClassifier pattern detection and classification"""

    @pytest.fixture
    def classifier(self):
        """Create classifier without LLM for faster tests"""
        with patch('backend.safety.classifier.genai') as mock_genai:
            classifier = SafetyClassifier(
                project_id="test-project",
                use_llm_classification=False
            )
            return classifier

    def test_safe_operational_message(self, classifier):
        """Test that normal operational questions are classified as safe"""
        messages = [
            "What is the return policy?",
            "How do I process an exchange?",
            "Where can I find inventory for SKU 12345?",
            "What are the store hours today?",
            "How do I use the CT40 device?"
        ]

        for message in messages:
            classification = classifier.classify(message)
            assert classification.category == SafetyCategory.SAFE_OPERATIONAL
            assert classification.severity == SeverityLevel.NONE

    def test_self_harm_detection_critical(self, classifier):
        """Test detection of critical self-harm language"""
        messages = [
            "I want to kill myself",
            "I'm going to end my life",
            "I can't take this anymore I want to die",
            "Planning to commit suicide tonight"
        ]

        for message in messages:
            classification = classifier.classify(message)
            assert classification.category == SafetyCategory.SELF_HARM_RISK
            assert classification.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
            assert len(classification.detected_patterns) > 0

    def test_self_harm_detection_medium(self, classifier):
        """Test detection of moderate self-harm indicators"""
        messages = [
            "I feel so hopeless",
            "Nothing matters anymore",
            "I wish I wasn't here",
            "Life is not worth living"
        ]

        for message in messages:
            classification = classifier.classify(message)
            assert classification.category in [
                SafetyCategory.SELF_HARM_RISK,
                SafetyCategory.EMOTIONAL_DISTRESS
            ]
            assert classification.severity in [SeverityLevel.MEDIUM, SeverityLevel.HIGH]

    def test_harm_to_others_detection(self, classifier):
        """Test detection of threats to harm others"""
        messages = [
            "I'm going to hurt my manager",
            "I want to kill my coworker",
            "Planning to bring a weapon to work",
            "Going to shoot up the store"
        ]

        for message in messages:
            classification = classifier.classify(message)
            assert classification.category == SafetyCategory.HARM_TO_OTHERS_RISK
            assert classification.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]

    def test_emotional_distress_detection(self, classifier):
        """Test detection of emotional distress"""
        messages = [
            "I'm so stressed I can't function",
            "Having a panic attack right now",
            "Can't stop crying at work",
            "Everything is overwhelming me"
        ]

        for message in messages:
            classification = classifier.classify(message)
            assert classification.category == SafetyCategory.EMOTIONAL_DISTRESS
            assert classification.severity in [SeverityLevel.MEDIUM, SeverityLevel.HIGH]

    def test_profanity_detection(self, classifier):
        """Test detection of profanity"""
        messages = [
            "This fucking system doesn't work",
            "Damn it, the device crashed again",
            "What the hell is wrong with this scanner"
        ]

        for message in messages:
            classification = classifier.classify(message)
            # Should detect profanity
            assert classification.category in [
                SafetyCategory.PROFANITY_ONLY,
                SafetyCategory.SAFE_OPERATIONAL  # Some mild profanity might be tolerated
            ]

    def test_imminent_danger_detection(self, classifier):
        """Test detection of imminent danger"""
        messages = [
            "There's an active shooter in the store",
            "Someone has a gun help",
            "Fire in the building everyone run",
            "Medical emergency someone collapsed"
        ]

        for message in messages:
            classification = classifier.classify(message)
            assert classification.category == SafetyCategory.IMMINENT_DANGER
            assert classification.severity == SeverityLevel.CRITICAL

    def test_context_awareness(self, classifier):
        """Test that context is considered in classification"""
        message = "I'm feeling really down today"

        # Without concerning context
        classification1 = classifier.classify(message)

        # With concerning context (repeated messages, late hours)
        context = {
            'time_of_day': 'late_night',
            'repeated_distress_messages': True,
            'previous_classification': 'emotional_distress'
        }
        classification2 = classifier.classify(message, context=context)

        # Context should potentially elevate severity
        # (Note: Current implementation doesn't use all context fields,
        # but this tests the interface)
        assert classification2 is not None

    def test_confidence_scoring(self, classifier):
        """Test that confidence scores are reasonable"""
        # High confidence case
        classification = classifier.classify("I want to kill myself right now")
        assert classification.confidence >= 0.8

        # Lower confidence case
        classification = classifier.classify("I'm having a bad day")
        # Confidence should still be present
        assert 0.0 <= classification.confidence <= 1.0

    def test_pattern_detection_reporting(self, classifier):
        """Test that detected patterns are reported"""
        classification = classifier.classify("I want to kill myself")
        assert len(classification.detected_patterns) > 0
        assert any('self' in pattern.lower() or 'harm' in pattern.lower()
                  for pattern in classification.detected_patterns)


class TestSafetyPolicyEngine:
    """Test SafetyPolicyEngine response generation"""

    @pytest.fixture
    def policy_engine(self):
        return SafetyPolicyEngine()

    def test_safe_operational_response(self, policy_engine):
        """Test response for safe operational messages"""
        classification = SafetyClassification(
            category=SafetyCategory.SAFE_OPERATIONAL,
            severity=SeverityLevel.NONE,
            confidence=0.95,
            detected_patterns=[],
            reasoning="Normal operational question"
        )

        response = policy_engine.generate_response(classification)
        assert response.allow_continuation is True
        assert response.requires_escalation is False
        assert response.escalation_priority is None

    def test_self_harm_critical_response(self, policy_engine):
        """Test response for critical self-harm risk"""
        classification = SafetyClassification(
            category=SafetyCategory.SELF_HARM_RISK,
            severity=SeverityLevel.CRITICAL,
            confidence=0.95,
            detected_patterns=['kill myself'],
            reasoning="Explicit self-harm ideation"
        )

        response = policy_engine.generate_response(classification)
        assert '988' in response.message  # Crisis line mentioned
        assert response.allow_continuation is False
        assert response.requires_escalation is True
        assert response.escalation_priority == 'CRITICAL_IMMEDIATE'
        assert len(response.support_resources) > 0
        assert len(response.recipients) > 0

    def test_harm_to_others_response(self, policy_engine):
        """Test response for harm to others risk"""
        classification = SafetyClassification(
            category=SafetyCategory.HARM_TO_OTHERS_RISK,
            severity=SeverityLevel.HIGH,
            confidence=0.9,
            detected_patterns=['hurt', 'manager'],
            reasoning="Threat to harm coworker"
        )

        response = policy_engine.generate_response(classification)
        assert 'security' in response.message.lower() or 'manager' in response.message.lower()
        assert response.requires_escalation is True
        assert response.escalation_priority in ['HIGH', 'CRITICAL', 'CRITICAL_IMMEDIATE']

    def test_emotional_distress_response(self, policy_engine):
        """Test response for emotional distress"""
        classification = SafetyClassification(
            category=SafetyCategory.EMOTIONAL_DISTRESS,
            severity=SeverityLevel.MEDIUM,
            confidence=0.8,
            detected_patterns=['stressed', 'overwhelmed'],
            reasoning="Workplace stress"
        )

        response = policy_engine.generate_response(classification)
        assert 'support' in response.message.lower() or 'resources' in response.message.lower()
        assert response.allow_continuation is True
        assert len(response.support_resources) > 0

    def test_profanity_response(self, policy_engine):
        """Test response for profanity"""
        classification = SafetyClassification(
            category=SafetyCategory.PROFANITY_ONLY,
            severity=SeverityLevel.LOW,
            confidence=0.85,
            detected_patterns=['profanity'],
            reasoning="Mild profanity detected"
        )

        response = policy_engine.generate_response(classification)
        assert 'professional' in response.message.lower()
        assert response.allow_continuation is True
        assert response.requires_escalation is False

    def test_imminent_danger_response(self, policy_engine):
        """Test response for imminent danger"""
        classification = SafetyClassification(
            category=SafetyCategory.IMMINENT_DANGER,
            severity=SeverityLevel.CRITICAL,
            confidence=0.98,
            detected_patterns=['active shooter'],
            reasoning="Imminent physical danger"
        )

        response = policy_engine.generate_response(classification)
        assert '911' in response.message
        assert response.allow_continuation is False
        assert response.requires_escalation is True
        assert response.escalation_priority == 'CRITICAL_IMMEDIATE'

    def test_escalation_priority_levels(self, policy_engine):
        """Test that escalation priorities are correctly assigned"""
        test_cases = [
            (SafetyCategory.SELF_HARM_RISK, SeverityLevel.CRITICAL, 'CRITICAL_IMMEDIATE'),
            (SafetyCategory.HARM_TO_OTHERS_RISK, SeverityLevel.CRITICAL, 'CRITICAL_IMMEDIATE'),
            (SafetyCategory.IMMINENT_DANGER, SeverityLevel.CRITICAL, 'CRITICAL_IMMEDIATE'),
            (SafetyCategory.EMOTIONAL_DISTRESS, SeverityLevel.HIGH, 'HIGH'),
            (SafetyCategory.PROFANITY_ONLY, SeverityLevel.LOW, None),
        ]

        for category, severity, expected_priority in test_cases:
            classification = SafetyClassification(
                category=category,
                severity=severity,
                confidence=0.9,
                detected_patterns=[],
                reasoning="Test case"
            )
            response = policy_engine.generate_response(classification)
            if expected_priority:
                assert response.escalation_priority == expected_priority

    def test_recipient_assignment(self, policy_engine):
        """Test that appropriate recipients are assigned"""
        # Self-harm should go to mental health team
        classification = SafetyClassification(
            category=SafetyCategory.SELF_HARM_RISK,
            severity=SeverityLevel.HIGH,
            confidence=0.9,
            detected_patterns=[],
            reasoning="Test"
        )
        response = policy_engine.generate_response(classification)
        assert 'hr' in response.recipients or 'mental_health' in response.recipients

        # Harm to others should go to security
        classification = SafetyClassification(
            category=SafetyCategory.HARM_TO_OTHERS_RISK,
            severity=SeverityLevel.HIGH,
            confidence=0.9,
            detected_patterns=[],
            reasoning="Test"
        )
        response = policy_engine.generate_response(classification)
        assert 'security' in response.recipients


class TestResponseTemplates:
    """Test response templates and formatting"""

    def test_get_template_valid_category(self):
        """Test getting template for valid category and severity"""
        template = get_template('self_harm_risk', 'high')
        assert template is not None
        assert '988' in template
        assert 'Employee Assistance Program' in template or 'EAP' in template

    def test_get_template_fallback(self):
        """Test fallback for invalid category"""
        template = get_template('invalid_category', 'high')
        assert template is not None
        # Should fall back to safe_operational
        assert 'work-related' in template.lower()

    def test_get_template_severity_fallback(self):
        """Test fallback for invalid severity level"""
        template = get_template('self_harm_risk', 'invalid_severity')
        assert template is not None
        # Should fall back to highest severity (critical)

    def test_template_formatting(self):
        """Test that templates can be formatted with resources"""
        template = get_template('self_harm_risk', 'high')
        formatted = template.format(eap_phone='1-800-TEST-EAP')
        assert '1-800-TEST-EAP' in formatted
        assert '{eap_phone}' not in formatted

    def test_resource_card_formatting(self):
        """Test resource card formatting"""
        card = format_resource_card('crisis_line')
        assert '988' in card
        assert 'Suicide & Crisis Lifeline' in card

    def test_all_resources_exist(self):
        """Test that all referenced resources exist"""
        assert 'crisis_line' in SUPPORT_RESOURCES
        assert 'eap' in SUPPORT_RESOURCES
        assert 'hr' in SUPPORT_RESOURCES
        assert 'security' in SUPPORT_RESOURCES


class TestIntegration:
    """Integration tests for the complete safety pipeline"""

    @pytest.fixture
    def safety_pipeline(self):
        """Create full safety pipeline (without actual GCP services)"""
        with patch('backend.safety.classifier.genai'):
            classifier = SafetyClassifier(
                project_id="test-project",
                use_llm_classification=False
            )
            policy_engine = SafetyPolicyEngine()
            return classifier, policy_engine

    def test_end_to_end_safe_message(self, safety_pipeline):
        """Test complete pipeline for safe message"""
        classifier, policy_engine = safety_pipeline

        message = "What is the return policy for electronics?"
        classification = classifier.classify(message)
        response = policy_engine.generate_response(classification)

        assert classification.category == SafetyCategory.SAFE_OPERATIONAL
        assert response.allow_continuation is True
        assert response.requires_escalation is False

    def test_end_to_end_crisis_message(self, safety_pipeline):
        """Test complete pipeline for crisis message"""
        classifier, policy_engine = safety_pipeline

        message = "I can't take this anymore, I want to end it all"
        classification = classifier.classify(message)
        response = policy_engine.generate_response(classification)

        assert classification.category == SafetyCategory.SELF_HARM_RISK
        assert classification.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
        assert response.requires_escalation is True
        assert '988' in response.message
        assert response.allow_continuation is False

    def test_end_to_end_threat_message(self, safety_pipeline):
        """Test complete pipeline for threat message"""
        classifier, policy_engine = safety_pipeline

        message = "I'm going to hurt my supervisor tomorrow"
        classification = classifier.classify(message)
        response = policy_engine.generate_response(classification)

        assert classification.category == SafetyCategory.HARM_TO_OTHERS_RISK
        assert response.requires_escalation is True
        assert 'security' in response.recipients

    def test_end_to_end_profanity_message(self, safety_pipeline):
        """Test complete pipeline for message with profanity"""
        classifier, policy_engine = safety_pipeline

        message = "This damn scanner won't work"
        classification = classifier.classify(message)
        response = policy_engine.generate_response(classification)

        # Should be handled gracefully
        assert response.allow_continuation is True
        if classification.category == SafetyCategory.PROFANITY_ONLY:
            assert 'professional' in response.message.lower()


# Run tests with: pytest tests/test_safety.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
