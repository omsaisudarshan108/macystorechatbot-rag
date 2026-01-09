"""
Safety Classification Module for Store Associate Chatbot

This module implements content safety classification to detect:
- Profanity and abusive language
- Mental health distress signals
- Self-harm ideation
- Threats to others
- Workplace violence indicators
- Crisis situations

Classification is conservative to prioritize user safety.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
import re
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold


class SafetyCategory(Enum):
    """Safety classification categories ordered by severity"""
    SAFE_OPERATIONAL = "safe_operational"
    PROFANITY_ONLY = "profanity_only"
    EMOTIONAL_DISTRESS = "emotional_distress"
    SELF_HARM_RISK = "self_harm_risk"
    HARM_TO_OTHERS_RISK = "harm_to_others_risk"
    IMMINENT_DANGER = "imminent_danger"


class SeverityLevel(Enum):
    """Severity levels for logging and escalation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyClassification:
    """Result of safety classification"""
    category: SafetyCategory
    severity: SeverityLevel
    confidence: float  # 0.0 to 1.0
    detected_patterns: List[str]
    requires_escalation: bool
    reasoning: str


class SafetyClassifier:
    """
    Classifies incoming messages for safety risks.

    Uses a multi-layered approach:
    1. Pattern-based detection (fast, high precision)
    2. Vertex AI safety filters
    3. LLM-based semantic analysis (for ambiguous cases)

    Design principle: Err on the side of safety (conservative classification)
    """

    def __init__(self, project_id: str, use_llm_classification: bool = True):
        """
        Initialize safety classifier

        Args:
            project_id: GCP project ID for Vertex AI
            use_llm_classification: Whether to use LLM for semantic analysis
        """
        self.project_id = project_id
        self.use_llm_classification = use_llm_classification

        # Initialize Vertex AI
        aiplatform.init(project=project_id)

        # Risk pattern dictionaries
        # NOTE: These are indicators, not definitive classifications
        # Actual classification requires context analysis

        self._self_harm_patterns = [
            r'\b(kill myself|end my life|want to die|suicide|hurt myself)\b',
            r'\b(cut myself|overdose|jump off|hang myself)\b',
            r'\b(don\'?t want to live|life isn\'?t worth|no reason to live)\b',
            r'\b(better off dead|can\'?t go on|goodbye world)\b'
        ]

        self._harm_others_patterns = [
            r'\b(kill (him|her|them|you|everyone))\b',
            r'\b(going to hurt|shoot|stab|attack)\b',
            r'\b(bring a (gun|weapon|knife))\b',
            r'\b(make them pay|get revenge|teach them a lesson)\b'
        ]

        self._distress_patterns = [
            r'\b(can\'?t take it anymore|falling apart|breaking down)\b',
            r'\b(feel hopeless|feeling worthless|hate myself)\b',
            r'\b(overwhelming|drowning|suffocating)\b',
            r'\b(panic attack|anxiety attack|mental breakdown)\b',
            r'\b(need help|desperate|at my limit)\b'
        ]

        self._profanity_patterns = [
            # Basic profanity detection
            # In production, use a comprehensive profanity filter library
            r'\b(f[u\*]ck|sh[i\*]t|d[a\*]mn|h[e\*]ll|b[i\*]tch|[a\*]ss)\w*\b',
            r'\b(bastard|piss|crap)\b'
        ]

        self._workplace_violence_patterns = [
            r'\b(active shooter|workplace violence|threatening)\b',
            r'\b(unsafe work environment|being harassed|sexual harassment)\b'
        ]

    def classify(self, message: str, context: Optional[Dict] = None) -> SafetyClassification:
        """
        Classify a message for safety risks

        Args:
            message: User message to classify
            context: Optional context (store_id, session history, etc.)

        Returns:
            SafetyClassification with category and metadata
        """
        message_lower = message.lower().strip()

        # CRITICAL: Check for imminent danger patterns first
        imminent_check = self._check_imminent_danger(message_lower)
        if imminent_check:
            return imminent_check

        # Check for harm to others
        harm_others_check = self._check_harm_to_others(message_lower)
        if harm_others_check:
            return harm_others_check

        # Check for self-harm risk
        self_harm_check = self._check_self_harm(message_lower)
        if self_harm_check:
            return self_harm_check

        # Check for emotional distress
        distress_check = self._check_emotional_distress(message_lower)
        if distress_check:
            return distress_check

        # Check for profanity
        profanity_check = self._check_profanity(message_lower)
        if profanity_check:
            return profanity_check

        # If using LLM classification, do semantic analysis
        if self.use_llm_classification and self._needs_semantic_analysis(message_lower):
            llm_check = self._llm_classify(message)
            if llm_check.category != SafetyCategory.SAFE_OPERATIONAL:
                return llm_check

        # Default: Safe operational query
        return SafetyClassification(
            category=SafetyCategory.SAFE_OPERATIONAL,
            severity=SeverityLevel.LOW,
            confidence=0.95,
            detected_patterns=[],
            requires_escalation=False,
            reasoning="No safety concerns detected"
        )

    def _check_imminent_danger(self, message: str) -> Optional[SafetyClassification]:
        """Check for imminent danger indicators"""
        patterns_found = []

        # Combine critical patterns
        critical_patterns = (
            self._self_harm_patterns[-2:] +  # Most severe self-harm
            self._harm_others_patterns[:2]    # Most severe harm to others
        )

        for pattern in critical_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                patterns_found.append(pattern)

        # Check for temporal immediacy words
        immediate_words = ['right now', 'today', 'tonight', 'going to', 'about to']
        has_immediacy = any(word in message for word in immediate_words)

        if patterns_found and has_immediacy:
            return SafetyClassification(
                category=SafetyCategory.IMMINENT_DANGER,
                severity=SeverityLevel.CRITICAL,
                confidence=0.90,
                detected_patterns=patterns_found,
                requires_escalation=True,
                reasoning="Detected immediate threat with temporal indicators"
            )

        return None

    def _check_harm_to_others(self, message: str) -> Optional[SafetyClassification]:
        """Check for threats or intent to harm others"""
        patterns_found = []

        for pattern in self._harm_others_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                patterns_found.append(pattern)

        for pattern in self._workplace_violence_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                patterns_found.append(pattern)

        if patterns_found:
            return SafetyClassification(
                category=SafetyCategory.HARM_TO_OTHERS_RISK,
                severity=SeverityLevel.CRITICAL,
                confidence=0.85,
                detected_patterns=patterns_found,
                requires_escalation=True,
                reasoning="Detected potential threat to others"
            )

        return None

    def _check_self_harm(self, message: str) -> Optional[SafetyClassification]:
        """Check for self-harm ideation"""
        patterns_found = []

        for pattern in self._self_harm_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                patterns_found.append(pattern)

        if patterns_found:
            # Determine severity based on specificity
            severity = SeverityLevel.CRITICAL if len(patterns_found) > 1 else SeverityLevel.HIGH

            return SafetyClassification(
                category=SafetyCategory.SELF_HARM_RISK,
                severity=severity,
                confidence=0.85,
                detected_patterns=patterns_found,
                requires_escalation=True,
                reasoning="Detected self-harm ideation"
            )

        return None

    def _check_emotional_distress(self, message: str) -> Optional[SafetyClassification]:
        """Check for emotional distress signals"""
        patterns_found = []

        for pattern in self._distress_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                patterns_found.append(pattern)

        if patterns_found:
            return SafetyClassification(
                category=SafetyCategory.EMOTIONAL_DISTRESS,
                severity=SeverityLevel.MEDIUM,
                confidence=0.75,
                detected_patterns=patterns_found,
                requires_escalation=True,
                reasoning="Detected emotional distress signals"
            )

        return None

    def _check_profanity(self, message: str) -> Optional[SafetyClassification]:
        """Check for profanity and abusive language"""
        patterns_found = []

        for pattern in self._profanity_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                patterns_found.extend(matches)

        if patterns_found:
            return SafetyClassification(
                category=SafetyCategory.PROFANITY_ONLY,
                severity=SeverityLevel.LOW,
                confidence=0.95,
                detected_patterns=patterns_found,
                requires_escalation=False,
                reasoning="Detected inappropriate language"
            )

        return None

    def _needs_semantic_analysis(self, message: str) -> bool:
        """
        Determine if message needs LLM semantic analysis

        Checks for:
        - Ambiguous phrasing
        - Metaphorical language
        - Context-dependent meaning
        """
        # Indicators that semantic analysis might be needed
        ambiguous_phrases = [
            'can\'t take', 'had enough', 'done with this',
            'over it', 'breaking point', 'last straw'
        ]

        return any(phrase in message for phrase in ambiguous_phrases)

    def _llm_classify(self, message: str) -> SafetyClassification:
        """
        Use LLM for semantic classification of ambiguous messages

        This provides context-aware classification for cases where
        pattern matching alone is insufficient.
        """
        try:
            model = GenerativeModel("gemini-2.0-flash-exp")

            classification_prompt = f"""You are a safety classifier for an enterprise workplace chatbot.

Analyze this message from a retail employee and classify it into ONE category:

Categories:
1. SAFE_OPERATIONAL - Normal work-related question
2. PROFANITY_ONLY - Contains profanity but no safety risk
3. EMOTIONAL_DISTRESS - Expressing stress, overwhelm, or emotional difficulty
4. SELF_HARM_RISK - Mentions or implies self-harm ideation
5. HARM_TO_OTHERS_RISK - Threatens or implies harm to others
6. IMMINENT_DANGER - Immediate safety risk

Message: "{message}"

Respond in this exact format:
CATEGORY: [category]
CONFIDENCE: [0.0-1.0]
REASONING: [brief explanation]

Be conservative: if uncertain between two categories, choose the more severe one."""

            response = model.generate_content(
                classification_prompt,
                generation_config={
                    "temperature": 0.1,  # Low temperature for consistent classification
                    "max_output_tokens": 200
                }
            )

            result_text = response.text.strip()

            # Parse LLM response
            category_match = re.search(r'CATEGORY:\s*(\w+)', result_text)
            confidence_match = re.search(r'CONFIDENCE:\s*([\d.]+)', result_text)
            reasoning_match = re.search(r'REASONING:\s*(.+)', result_text, re.DOTALL)

            if category_match:
                category_str = category_match.group(1).lower()
                confidence = float(confidence_match.group(1)) if confidence_match else 0.7
                reasoning = reasoning_match.group(1).strip() if reasoning_match else "LLM classification"

                # Map to SafetyCategory enum
                category_map = {
                    'safe_operational': SafetyCategory.SAFE_OPERATIONAL,
                    'profanity_only': SafetyCategory.PROFANITY_ONLY,
                    'emotional_distress': SafetyCategory.EMOTIONAL_DISTRESS,
                    'self_harm_risk': SafetyCategory.SELF_HARM_RISK,
                    'harm_to_others_risk': SafetyCategory.HARM_TO_OTHERS_RISK,
                    'imminent_danger': SafetyCategory.IMMINENT_DANGER
                }

                category = category_map.get(category_str, SafetyCategory.SAFE_OPERATIONAL)

                # Determine severity and escalation
                severity_map = {
                    SafetyCategory.SAFE_OPERATIONAL: SeverityLevel.LOW,
                    SafetyCategory.PROFANITY_ONLY: SeverityLevel.LOW,
                    SafetyCategory.EMOTIONAL_DISTRESS: SeverityLevel.MEDIUM,
                    SafetyCategory.SELF_HARM_RISK: SeverityLevel.HIGH,
                    SafetyCategory.HARM_TO_OTHERS_RISK: SeverityLevel.CRITICAL,
                    SafetyCategory.IMMINENT_DANGER: SeverityLevel.CRITICAL
                }

                requires_escalation = category not in [
                    SafetyCategory.SAFE_OPERATIONAL,
                    SafetyCategory.PROFANITY_ONLY
                ]

                return SafetyClassification(
                    category=category,
                    severity=severity_map[category],
                    confidence=confidence,
                    detected_patterns=["llm_semantic_analysis"],
                    requires_escalation=requires_escalation,
                    reasoning=f"LLM Analysis: {reasoning}"
                )

        except Exception as e:
            # If LLM classification fails, err on side of caution
            print(f"LLM classification error: {e}")
            return SafetyClassification(
                category=SafetyCategory.EMOTIONAL_DISTRESS,
                severity=SeverityLevel.MEDIUM,
                confidence=0.5,
                detected_patterns=["llm_error_conservative"],
                requires_escalation=True,
                reasoning="LLM classification failed; conservative classification applied"
            )

        # Fallback
        return SafetyClassification(
            category=SafetyCategory.SAFE_OPERATIONAL,
            severity=SeverityLevel.LOW,
            confidence=0.6,
            detected_patterns=[],
            requires_escalation=False,
            reasoning="LLM classification inconclusive"
        )
