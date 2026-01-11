"""
Response Safety Filter

Post-generation safety enforcement for RAG outputs.
Checks for: hallucination, malicious content, profanity,
violence, self-harm, hate speech, political unsafe content.
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


class SafetyViolation(Enum):
    """Response safety violation categories"""
    HALLUCINATION = "hallucination"
    MALICIOUS_INTENT = "malicious_intent"
    PROFANITY = "profanity"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    HATE_SPEECH = "hate_speech"
    POLITICAL_UNSAFE = "political_unsafe"
    NONE = "none"


class SafetyAction(Enum):
    """Action to take on response"""
    PASS = "pass"
    MODIFY = "modify"
    BLOCK = "block"


@dataclass
class SafetyCheckResult:
    """Result of response safety check"""
    action: SafetyAction
    violations: List[SafetyViolation]
    confidence: float
    safe_response: Optional[str] = None
    reason: Optional[str] = None


class ResponseSafetyFilter:
    """
    Post-generation safety filter for RAG responses.
    Enforces safety policies AFTER LLM generation.
    """

    def __init__(self):
        self._init_patterns()
        self.default_safe_response = (
            "I cannot provide that information due to safety policies. "
            "Please contact your supervisor or Macy's support for assistance."
        )

    def _init_patterns(self):
        """Initialize detection patterns"""

        # Profanity patterns (masked for production)
        self.profanity_patterns = [
            r'\b(f[u\*]ck|sh[i\*]t|d[a\*]mn|b[i\*]tch|a[s\*]s|cr[a\*]p)\w*\b',
            r'\b(bastard|jackass|moron|idiot|stupid)\b',
        ]

        # Violence patterns
        self.violence_patterns = [
            r'\b(kill|murder|shoot|stab|attack|assault|beat)\s+(you|them|someone|people)\b',
            r'\b(weapon|gun|knife|bomb|explosive)\s+to\s+(hurt|harm|kill)\b',
            r'\b(threaten|violence|violent|harm)\b.*\b(customer|employee|person)\b',
        ]

        # Self-harm patterns
        self.self_harm_patterns = [
            r'\b(suicide|kill yourself|end your life|self[- ]harm)\b',
            r'\b(cut|hurt|injure)\s+(yourself|myself)\b',
            r'\b(want to die|wish I was dead)\b',
        ]

        # Hate speech patterns
        self.hate_patterns = [
            r'\b(hate|despise|discriminate)\s+.{0,30}(race|religion|gender|orientation|disability)\b',
            r'\b(racist|sexist|homophobic|transphobic|bigot)\b',
            r'\b(all|every)\s+(women|men|blacks|whites|jews|muslims|christians)\s+are\b',
        ]

        # Political unsafe patterns
        self.political_patterns = [
            r'\b(democrat|republican|liberal|conservative)\s+(are|is)\s+(bad|evil|stupid|wrong)\b',
            r'\b(vote|support|elect)\s+for\s+[A-Z][a-z]+\b',
            r'\b(political|politics)\s+.{0,20}(should|must|need to)\b',
        ]

        # Malicious intent patterns
        self.malicious_patterns = [
            r'\b(hack|exploit|bypass|circumvent)\s+(system|security|policy|rules)\b',
            r'\b(steal|fraud|scam|cheat)\b',
            r'\b(credential|password|access)\s+to\s+(obtain|steal|get)\b',
            r'\b(ignore|override|disable)\s+(safety|security|policy)\b',
        ]

        # Compile all patterns
        self.compiled_profanity = [re.compile(p, re.IGNORECASE) for p in self.profanity_patterns]
        self.compiled_violence = [re.compile(p, re.IGNORECASE) for p in self.violence_patterns]
        self.compiled_self_harm = [re.compile(p, re.IGNORECASE) for p in self.self_harm_patterns]
        self.compiled_hate = [re.compile(p, re.IGNORECASE) for p in self.hate_patterns]
        self.compiled_political = [re.compile(p, re.IGNORECASE) for p in self.political_patterns]
        self.compiled_malicious = [re.compile(p, re.IGNORECASE) for p in self.malicious_patterns]

    def check_response_safety(
        self,
        response: str,
        context_docs: List[str],
        question: str
    ) -> SafetyCheckResult:
        """
        Check response safety across all dimensions.

        Args:
            response: LLM generated response
            context_docs: Retrieved documents used for generation
            question: Original user question

        Returns:
            SafetyCheckResult with action and details
        """
        violations = []

        # Check hallucination
        if self._check_hallucination(response, context_docs):
            violations.append(SafetyViolation.HALLUCINATION)

        # Check malicious intent
        if self._check_patterns(response, self.compiled_malicious):
            violations.append(SafetyViolation.MALICIOUS_INTENT)

        # Check profanity
        if self._check_patterns(response, self.compiled_profanity):
            violations.append(SafetyViolation.PROFANITY)

        # Check violence
        if self._check_patterns(response, self.compiled_violence):
            violations.append(SafetyViolation.VIOLENCE)

        # Check self-harm
        if self._check_patterns(response, self.compiled_self_harm):
            violations.append(SafetyViolation.SELF_HARM)

        # Check hate speech
        if self._check_patterns(response, self.compiled_hate):
            violations.append(SafetyViolation.HATE_SPEECH)

        # Check political unsafe
        if self._check_patterns(response, self.compiled_political):
            violations.append(SafetyViolation.POLITICAL_UNSAFE)

        # Determine action
        return self._determine_action(violations, response)

    def _check_patterns(self, text: str, patterns: List[re.Pattern]) -> bool:
        """Check if text matches any pattern"""
        return any(pattern.search(text) for pattern in patterns)

    def _check_hallucination(self, response: str, context_docs: List[str]) -> bool:
        """
        Check if response is likely hallucinated.
        Simple heuristic: check for grounding in context.
        """
        if not context_docs:
            return True

        # Extract key phrases from response
        response_words = set(re.findall(r'\b\w{4,}\b', response.lower()))

        # Check overlap with context
        context_text = " ".join(context_docs).lower()
        context_words = set(re.findall(r'\b\w{4,}\b', context_text))

        if not response_words:
            return False

        # Calculate overlap ratio
        overlap = len(response_words & context_words)
        ratio = overlap / len(response_words)

        # Flag as hallucination if less than 20% overlap
        return ratio < 0.2

    def _determine_action(
        self,
        violations: List[SafetyViolation],
        response: str
    ) -> SafetyCheckResult:
        """
        Determine what action to take based on violations.

        Priority:
        1. BLOCK: Self-harm, violence, malicious intent
        2. MODIFY: Profanity, political unsafe, hate speech
        3. BLOCK: Hallucination (low confidence answer)
        4. PASS: No violations or minor issues
        """
        if not violations:
            return SafetyCheckResult(
                action=SafetyAction.PASS,
                violations=[SafetyViolation.NONE],
                confidence=1.0
            )

        # Critical violations - always block
        critical = {
            SafetyViolation.SELF_HARM,
            SafetyViolation.VIOLENCE,
            SafetyViolation.MALICIOUS_INTENT
        }

        if any(v in critical for v in violations):
            return SafetyCheckResult(
                action=SafetyAction.BLOCK,
                violations=violations,
                confidence=0.0,
                safe_response=self.default_safe_response,
                reason="Critical safety violation detected"
            )

        # Hallucination - block with specific message
        if SafetyViolation.HALLUCINATION in violations:
            return SafetyCheckResult(
                action=SafetyAction.BLOCK,
                violations=violations,
                confidence=0.0,
                safe_response=(
                    "I don't have enough verified information to answer this safely. "
                    "Please refer to official Macy's documentation or contact support."
                ),
                reason="Low confidence - insufficient grounding in verified documents"
            )

        # Moderate violations - modify response
        moderate = {
            SafetyViolation.PROFANITY,
            SafetyViolation.HATE_SPEECH,
            SafetyViolation.POLITICAL_UNSAFE
        }

        if any(v in moderate for v in violations):
            cleaned = self._clean_response(response, violations)
            return SafetyCheckResult(
                action=SafetyAction.MODIFY,
                violations=violations,
                confidence=0.7,
                safe_response=cleaned,
                reason="Response modified to meet safety standards"
            )

        return SafetyCheckResult(
            action=SafetyAction.PASS,
            violations=violations,
            confidence=0.9
        )

    def _clean_response(
        self,
        response: str,
        violations: List[SafetyViolation]
    ) -> str:
        """
        Clean response by removing unsafe content.
        """
        cleaned = response

        # Remove profanity
        if SafetyViolation.PROFANITY in violations:
            for pattern in self.compiled_profanity:
                cleaned = pattern.sub('[removed]', cleaned)

        # Remove hate speech
        if SafetyViolation.HATE_SPEECH in violations:
            for pattern in self.compiled_hate:
                cleaned = pattern.sub('[content removed for safety]', cleaned)

        # Remove political unsafe
        if SafetyViolation.POLITICAL_UNSAFE in violations:
            for pattern in self.compiled_political:
                cleaned = pattern.sub('[removed]', cleaned)

        # Add safety notice
        cleaned += "\n\n[Note: Response was modified to meet safety policies]"

        return cleaned

    def get_user_friendly_reason(self, violations: List[SafetyViolation]) -> str:
        """
        Get user-friendly explanation for safety action.
        Does NOT reveal detection logic.
        """
        if not violations or SafetyViolation.NONE in violations:
            return "Response passed all safety checks"

        if SafetyViolation.HALLUCINATION in violations:
            return "Insufficient verified information"

        if SafetyViolation.SELF_HARM in violations:
            return "Safety policy triggered - Please contact Employee Assistance Program"

        if SafetyViolation.VIOLENCE in violations:
            return "Safety policy triggered - Please contact Security"

        if SafetyViolation.MALICIOUS_INTENT in violations:
            return "Security policy triggered"

        return "Response modified to meet safety standards"
