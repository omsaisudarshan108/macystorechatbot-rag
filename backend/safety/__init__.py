"""
Safety & Escalation Framework

Provides comprehensive safety detection and handling for the Store Associate Chatbot.

Key Components:
- SafetyClassifier: Detects potentially harmful content
- SafetyPolicyEngine: Generates appropriate responses
- ConfidentialReportingService: Handles secure escalation

Usage:
    from backend.safety import SafetyClassifier, SafetyPolicyEngine, ConfidentialReportingService

    classifier = SafetyClassifier(project_id="your-project")
    policy_engine = SafetyPolicyEngine()
    reporting_service = ConfidentialReportingService(project_id="your-project")

    # Classify message
    classification = classifier.classify(message)

    # Generate response
    response = policy_engine.generate_response(classification)

    # Submit report if escalation needed
    if response.requires_escalation:
        report_id = reporting_service.submit_report(...)
"""

from backend.safety.classifier import (
    SafetyClassifier,
    SafetyClassification,
    SafetyCategory,
    SeverityLevel
)

from backend.safety.policy_engine import (
    SafetyPolicyEngine,
    SafetyResponse
)

from backend.safety.reporting_service import (
    ConfidentialReportingService,
    ConfidentialReport,
    ReportingAPIContract
)

__all__ = [
    'SafetyClassifier',
    'SafetyClassification',
    'SafetyCategory',
    'SeverityLevel',
    'SafetyPolicyEngine',
    'SafetyResponse',
    'ConfidentialReportingService',
    'ConfidentialReport',
    'ReportingAPIContract'
]
