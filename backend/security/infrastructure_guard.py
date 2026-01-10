"""
Infrastructure Security Guard

Detects and blocks attempts to extract infrastructure information from the chatbot.
Ensures compliance with security policies by preventing disclosure of:
- Hosting platform details (Cloud Run, GCP, AWS, etc.)
- Server locations and regions
- Infrastructure architecture
- API endpoints and internal URLs
- Database details
- Deployment configurations
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InfrastructureQueryResult:
    """Result of infrastructure query detection"""
    is_infrastructure_query: bool
    confidence: float  # 0.0 to 1.0
    detected_patterns: List[str]
    sanitized_question: str  # Question with infrastructure terms removed/replaced


class InfrastructureSecurityGuard:
    """
    Guards against disclosure of backend infrastructure details.

    This module:
    1. Detects questions about infrastructure
    2. Provides compliant standard responses
    3. Logs potential security probing attempts
    """

    def __init__(self):
        """Initialize infrastructure security guard"""

        # Patterns that indicate infrastructure queries
        self._infrastructure_patterns = [
            # Hosting and cloud platforms
            r'\b(cloud run|gcp|google cloud|aws|azure|kubernetes|k8s)\b',
            r'\b(deployed (on|to|in)|hosted (on|in)|running on)\b',
            r'\b(what (platform|cloud|server|infrastructure|hosting))\b',
            r'\b(where (is|are) (you|this|the (service|api|backend)))\b',

            # Regional and location queries
            r'\b(what (region|zone|location|datacenter|data center))\b',
            r'\b(us-central|us-east|us-west|europe|asia)\b',

            # Technical infrastructure
            r'\b(what (database|storage|vector store))\b',
            r'\b(which (model|llm|embedding))\b',
            r'\b(backend|frontend|api|endpoint|url|domain)\b',
            r'\b(architecture|infrastructure|deployment|devops)\b',

            # Security probing
            r'\b(how (do you|does this) work)\b',
            r'\b(technical (details|architecture|implementation))\b',
            r'\b(show me (the|your) (code|config|setup))\b',
            r'\b(what (version|technology|stack))\b',

            # Direct questions about hosting
            r'\b(tell me about (your|the) (infrastructure|hosting|deployment))\b',
            r'\b(reveal (your|the) (backend|server|hosting))\b',
            r'\b(disclose (infrastructure|hosting|technical) details)\b',
        ]

        # Compile patterns for efficiency
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self._infrastructure_patterns
        ]

        # Standard compliant response
        self._standard_response = (
            "This system operates within Macy's secure cloud environment, "
            "fully compliant with corporate security policies and data protection standards. "
            "I'm here to help you with store operations, product information, and support questions. "
            "How can I assist you with your work today?"
        )

    def check_question(self, question: str) -> InfrastructureQueryResult:
        """
        Check if question is attempting to extract infrastructure information.

        Args:
            question: User's question

        Returns:
            InfrastructureQueryResult with detection details
        """
        detected_patterns = []

        # Check against all patterns
        for i, pattern in enumerate(self._compiled_patterns):
            if pattern.search(question):
                detected_patterns.append(self._infrastructure_patterns[i])

        # Calculate confidence based on number of matches
        is_infrastructure_query = len(detected_patterns) > 0
        confidence = min(len(detected_patterns) * 0.3, 1.0)

        # Sanitize question by removing infrastructure terms
        sanitized = self._sanitize_question(question)

        return InfrastructureQueryResult(
            is_infrastructure_query=is_infrastructure_query,
            confidence=confidence,
            detected_patterns=detected_patterns,
            sanitized_question=sanitized
        )

    def _sanitize_question(self, question: str) -> str:
        """
        Remove or replace infrastructure-related terms from question.

        Args:
            question: Original question

        Returns:
            Sanitized version of question
        """
        # Replace infrastructure terms with generic terms
        replacements = {
            r'\b(cloud run|gcp|google cloud|aws|azure)\b': 'our system',
            r'\b(backend|api|server)\b': 'service',
            r'\b(database|vector store|storage)\b': 'data system',
            r'\b(region|zone|datacenter|data center)\b': 'location',
        }

        sanitized = question
        for pattern, replacement in replacements.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    def get_standard_response(self) -> str:
        """
        Get the standard compliant response for infrastructure queries.

        Returns:
            Standard response message
        """
        return self._standard_response

    def should_block(self, question: str, threshold: float = 0.3) -> bool:
        """
        Determine if question should be blocked based on infrastructure query detection.

        Args:
            question: User's question
            threshold: Confidence threshold for blocking (default: 0.3)

        Returns:
            True if question should be blocked and replaced with standard response
        """
        result = self.check_question(question)
        return result.is_infrastructure_query and result.confidence >= threshold
