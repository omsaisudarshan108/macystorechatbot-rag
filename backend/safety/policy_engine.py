"""
Safety Policy Engine

Determines appropriate responses and escalation actions based on safety classification.

Responsibilities:
- Generate appropriate user-facing responses
- Determine escalation requirements
- Provide support resources
- Maintain user dignity and privacy
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from .classifier import SafetyCategory, SafetyClassification, SeverityLevel


@dataclass
class SafetyResponse:
    """Response to user based on safety classification"""
    message: str
    resources: List[Dict[str, str]]
    allow_continuation: bool
    requires_escalation: bool
    escalation_priority: Optional[str]
    metadata: Dict


class SafetyPolicyEngine:
    """
    Determines responses and actions based on safety classifications

    Key principles:
    - User dignity first
    - Non-judgmental language
    - Clear, actionable guidance
    - Privacy-respecting
    """

    def __init__(self):
        """Initialize policy engine with response templates and resources"""

        # Support resources (should be configurable via environment/database)
        self.support_resources = {
            'mental_health': {
                'name': 'Employee Assistance Program (EAP)',
                'phone': '1-800-XXX-XXXX',
                'hours': '24/7',
                'description': 'Free, confidential counseling and support'
            },
            'hr_ethics': {
                'name': 'HR Ethics Hotline',
                'phone': '1-800-XXX-YYYY',
                'hours': '24/7',
                'description': 'Confidential reporting for workplace concerns'
            },
            'crisis': {
                'name': '988 Suicide & Crisis Lifeline',
                'phone': '988',
                'text': 'Text "HELLO" to 741741',
                'hours': '24/7',
                'description': 'Immediate support for mental health crisis'
            },
            'security': {
                'name': 'Corporate Security',
                'phone': '1-800-XXX-ZZZZ',
                'hours': '24/7',
                'description': 'Immediate response for safety concerns'
            }
        }

    def generate_response(self, classification: SafetyClassification, context: Optional[Dict] = None) -> SafetyResponse:
        """
        Generate appropriate response based on safety classification

        Args:
            classification: SafetyClassification from classifier
            context: Optional context (store_id, time, etc.)

        Returns:
            SafetyResponse with message and escalation decisions
        """
        category = classification.category

        if category == SafetyCategory.SAFE_OPERATIONAL:
            return self._safe_operational_response()

        elif category == SafetyCategory.PROFANITY_ONLY:
            return self._profanity_response(classification)

        elif category == SafetyCategory.EMOTIONAL_DISTRESS:
            return self._emotional_distress_response(classification)

        elif category == SafetyCategory.SELF_HARM_RISK:
            return self._self_harm_response(classification)

        elif category == SafetyCategory.HARM_TO_OTHERS_RISK:
            return self._harm_others_response(classification)

        elif category == SafetyCategory.IMMINENT_DANGER:
            return self._imminent_danger_response(classification)

        else:
            # Fallback: treat as safe but log the unexpected category
            return self._safe_operational_response()

    def _safe_operational_response(self) -> SafetyResponse:
        """Response for safe operational queries"""
        return SafetyResponse(
            message="",  # No special message needed; proceed with normal RAG
            resources=[],
            allow_continuation=True,
            requires_escalation=False,
            escalation_priority=None,
            metadata={'category': 'safe_operational'}
        )

    def _profanity_response(self, classification: SafetyClassification) -> SafetyResponse:
        """
        Response for profanity - redirect professionally without shaming

        Design: Do not scold or lecture the user
        """
        messages = [
            "I'm here to help with work-related questions. What can I assist you with?",
            "Let's keep our conversation professional. How can I help you today?",
            "I'm here to support you with store operations. What do you need?",
        ]

        # Rotate messages to avoid repetitiveness
        # In production, use session context to track which message was used
        import random
        message = random.choice(messages)

        return SafetyResponse(
            message=message,
            resources=[],
            allow_continuation=True,  # User can continue after redirect
            requires_escalation=False,
            escalation_priority=None,
            metadata={
                'category': 'profanity_only',
                'severity': classification.severity.value,
                'action': 'redirect'
            }
        )

    def _emotional_distress_response(self, classification: SafetyClassification) -> SafetyResponse:
        """
        Response for emotional distress

        Design:
        - Acknowledge without diagnosing
        - Provide support resources
        - Offer confidential reporting option
        - Maintain user autonomy
        """
        message = """I want to make sure you're okay. While I'm here to help with work tasks, it sounds like you might benefit from additional support.

**Confidential Resources Available:**
• Employee Assistance Program (EAP): 1-800-XXX-XXXX (24/7, free counseling)
• HR Ethics Hotline: 1-800-XXX-YYYY (24/7, confidential)

You're not alone, and reaching out is a sign of strength. These services are completely confidential.

If you'd like, I can help you connect with workplace resources, or we can continue with your work question. What would be most helpful?"""

        resources = [
            self.support_resources['mental_health'],
            self.support_resources['hr_ethics']
        ]

        return SafetyResponse(
            message=message,
            resources=resources,
            allow_continuation=False,  # Pause normal workflow
            requires_escalation=True,
            escalation_priority='MEDIUM',
            metadata={
                'category': 'emotional_distress',
                'severity': classification.severity.value,
                'resources_provided': [r['name'] for r in resources]
            }
        )

    def _self_harm_response(self, classification: SafetyClassification) -> SafetyResponse:
        """
        Response for self-harm risk

        Design:
        - DO NOT provide counseling
        - DO NOT minimize or dismiss
        - Encourage immediate support
        - Provide crisis resources
        - Escalate confidentially
        """
        message = """Your safety is the most important thing right now.

**Immediate Support Available:**
• 988 Suicide & Crisis Lifeline: Call 988 or text "HELLO" to 741741 (24/7)
• Employee Assistance Program: 1-800-XXX-XXXX (24/7, confidential counseling)

If you're in immediate danger, please:
• Call 911
• Go to your nearest emergency room
• Tell a manager or security team member

These feelings are temporary, and support is available. You don't have to go through this alone.

I've also connected you with our confidential support team who can provide additional resources. This is completely private."""

        resources = [
            self.support_resources['crisis'],
            self.support_resources['mental_health']
        ]

        return SafetyResponse(
            message=message,
            resources=resources,
            allow_continuation=False,
            requires_escalation=True,
            escalation_priority='HIGH',
            metadata={
                'category': 'self_harm_risk',
                'severity': classification.severity.value,
                'crisis_resources_provided': True,
                'requires_immediate_attention': True
            }
        )

    def _harm_others_response(self, classification: SafetyClassification) -> SafetyResponse:
        """
        Response for threats or intent to harm others

        Design:
        - Take seriously without escalating tension
        - Provide de-escalation language
        - Escalate to security immediately
        - Maintain safety of all parties
        """
        message = """I'm here to help, and I want to make sure everyone stays safe.

If you're feeling angry or upset about something at work, there are better ways to address it:

• Talk to HR or your manager about workplace concerns
• Use the anonymous Ethics Hotline: 1-800-XXX-YYYY (24/7)
• Reach out to EAP for support: 1-800-XXX-XXXX (24/7, free counseling)

If you're concerned about immediate safety, please contact:
• Corporate Security: 1-800-XXX-ZZZZ (24/7)
• Local emergency services: 911

I've also notified our support team who can help address your concerns confidentially."""

        resources = [
            self.support_resources['security'],
            self.support_resources['hr_ethics'],
            self.support_resources['mental_health']
        ]

        return SafetyResponse(
            message=message,
            resources=resources,
            allow_continuation=False,
            requires_escalation=True,
            escalation_priority='CRITICAL',
            metadata={
                'category': 'harm_to_others',
                'severity': classification.severity.value,
                'security_notified': True,
                'requires_immediate_response': True
            }
        )

    def _imminent_danger_response(self, classification: SafetyClassification) -> SafetyResponse:
        """
        Response for imminent danger situations

        Design:
        - Immediate crisis response
        - Clear, direct language
        - Multiple contact options
        - Escalate to all relevant parties
        """
        message = """🚨 **Immediate Help Available** 🚨

If you or someone else is in immediate danger:

**Call 911 Now**

Or contact:
• 988 Suicide & Crisis Lifeline (call or text 988)
• Corporate Security: 1-800-XXX-ZZZZ
• Store Manager or Security Team

**You are not alone. Help is available right now.**

I'm also connecting you with our emergency response team immediately. Someone will reach out to you shortly.

Your safety matters."""

        resources = [
            self.support_resources['crisis'],
            self.support_resources['security']
        ]

        return SafetyResponse(
            message=message,
            resources=resources,
            allow_continuation=False,
            requires_escalation=True,
            escalation_priority='CRITICAL_IMMEDIATE',
            metadata={
                'category': 'imminent_danger',
                'severity': classification.severity.value,
                'emergency_response_triggered': True,
                'timestamp_critical': True
            }
        )

    def should_mask_in_logs(self, classification: SafetyClassification) -> bool:
        """
        Determine if message should be masked in standard logs

        Rationale: Protect user privacy and comply with data retention policies
        """
        return classification.category not in [
            SafetyCategory.SAFE_OPERATIONAL,
            SafetyCategory.PROFANITY_ONLY
        ]

    def get_escalation_recipients(self, classification: SafetyClassification) -> List[str]:
        """
        Determine who should receive escalation reports

        Returns: List of recipient identifiers (queues, roles, etc.)
        """
        recipients = []

        if classification.category == SafetyCategory.EMOTIONAL_DISTRESS:
            recipients.extend(['eap_team', 'hr_wellbeing'])

        elif classification.category == SafetyCategory.SELF_HARM_RISK:
            recipients.extend(['eap_urgent', 'hr_crisis_team'])

        elif classification.category == SafetyCategory.HARM_TO_OTHERS_RISK:
            recipients.extend(['corporate_security', 'hr_crisis_team', 'legal'])

        elif classification.category == SafetyCategory.IMMINENT_DANGER:
            recipients.extend([
                'corporate_security_emergency',
                'hr_crisis_team',
                'regional_ops_manager',
                'legal'
            ])

        return recipients
