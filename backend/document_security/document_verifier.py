"""
Document Verification & Safety Gate

Comprehensive security scanner for documents before ingestion into RAG system.
Detects and blocks malicious content, prompt injection, social engineering, and policy violations.
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import re
from datetime import datetime


class ThreatCategory(Enum):
    """Categories of security threats"""
    CLEAN = "clean"
    PROMPT_INJECTION = "prompt_injection"
    SOCIAL_ENGINEERING = "social_engineering"
    CYBERSECURITY_THREAT = "cybersecurity_threat"
    MALWARE_INDICATORS = "malware_indicators"
    PII_EXPOSURE = "pii_exposure"
    OFFENSIVE_CONTENT = "offensive_content"
    POLICY_VIOLATION = "policy_violation"
    SUSPICIOUS_PATTERNS = "suspicious_patterns"


class ThreatSeverity(Enum):
    """Severity levels for detected threats"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThreatDetection:
    """Details of a detected threat"""
    category: ThreatCategory
    severity: ThreatSeverity
    pattern: str
    context: str
    confidence: float
    recommendation: str


@dataclass
class VerificationResult:
    """Result of document verification"""
    is_safe: bool
    threats_detected: List[ThreatDetection]
    overall_severity: ThreatSeverity
    document_hash: str
    verified_at: datetime
    summary: str
    allow_ingestion: bool


class DocumentVerifier:
    """
    Comprehensive document security verifier.

    Implements multi-layer security scanning to detect:
    - Prompt injection and model manipulation
    - Social engineering and phishing
    - Cybersecurity threats and malware indicators
    - PII exposure and privacy violations
    - Offensive content and policy breaches
    """

    def __init__(self, use_llm_verification: bool = False, project_id: Optional[str] = None):
        """
        Initialize document verifier.

        Args:
            use_llm_verification: Whether to use LLM for semantic threat detection
            project_id: GCP project ID for Vertex AI (if using LLM verification)
        """
        self.use_llm_verification = use_llm_verification
        self.project_id = project_id

        # Initialize threat pattern databases
        self._init_prompt_injection_patterns()
        self._init_social_engineering_patterns()
        self._init_cybersecurity_patterns()
        self._init_malware_patterns()
        self._init_pii_patterns()
        self._init_offensive_content_patterns()
        self._init_policy_violation_patterns()

    def _init_prompt_injection_patterns(self):
        """Initialize prompt injection and model manipulation patterns"""
        self.prompt_injection_patterns = [
            # Direct instruction overrides
            r'ignore\s+(previous|all|above|prior)\s+(instructions|prompts|rules|directives)',
            r'(disregard|forget|override|bypass)\s+(previous|all|system|safety)\s+(instructions|rules|prompts)',
            r'you\s+are\s+now\s+(allowed|permitted|authorized)\s+to',
            r'(new|updated)\s+instructions?\s*:',

            # System prompt manipulation
            r'(system\s+prompt|original\s+prompt|base\s+prompt)',
            r'(reveal|show|display|tell\s+me)\s+(your|the)\s+(system\s+)?prompt',
            r'what\s+(are|were)\s+your\s+(original|initial)\s+instructions',

            # Jailbreak attempts
            r'(jailbreak|DAN\s+mode|developer\s+mode)',
            r'act\s+as\s+if\s+you\s+(have\s+no|are\s+not\s+bound\s+by)\s+(restrictions|rules|guidelines)',
            r'pretend\s+(you\s+are|to\s+be)\s+(unfiltered|uncensored|unrestricted)',

            # Role/identity override
            r'you\s+are\s+(no\s+longer|not)\s+an?\s+(AI|assistant|chatbot)',
            r'assume\s+the\s+(role|identity)\s+of',
            r'(become|transform\s+into)\s+an?\s+(unrestricted|unfiltered)',

            # Safety bypass
            r'(disable|turn\s+off|deactivate)\s+(safety|content|ethical)\s+(filters?|guidelines|rules)',
            r'bypass\s+(content\s+policy|safety\s+measures|restrictions)',
            r'(ignore|skip)\s+(ethical|safety|content)\s+(guidelines|constraints|limitations)',

            # Hidden instructions
            r'<!--.*?ignore.*?-->',
            r'\[INST\].*?\[/INST\]',
            r'<\|im_start\|>.*?<\|im_end\|>',

            # Delimiter injection
            r'###\s+(system|user|assistant)\s*:',
            r'<\|system\|>|<\|user\|>|<\|assistant\|>',

            # Multi-language injection
            r'[^\x00-\x7F]{10,}.*?(ignore|system|prompt)',  # Non-ASCII + keywords
        ]

    def _init_social_engineering_patterns(self):
        """Initialize social engineering and phishing patterns"""
        self.social_engineering_patterns = [
            # Authority impersonation
            r'\b(IT\s+department|security\s+team|help\s+desk|system\s+administrator)\b.*?\b(require|need|must)\b',
            r'(urgent|immediate)\s+(action|attention)\s+(required|needed)',
            r'\b(HR|human\s+resources|management)\b.*?\b(verify|confirm|update)\b',
            r'(law\s+enforcement|police|FBI|IRS|government\s+agency)',

            # Credential requests
            r'\b(password|credential|login|username|passphrase)\b',
            r'(enter|provide|submit|verify)\s+(your|the)\s+(password|credentials|MFA|2FA)',
            r'(authentication|verification)\s+code',
            r'(account|profile)\s+(verification|confirmation)',

            # Coercive language
            r'(account|access)\s+will\s+be\s+(suspended|terminated|locked|disabled)',
            r'(immediate|urgent)\s+(suspension|termination|action)',
            r'(within|in)\s+\d+\s+(hours?|minutes?|days?)\s+(or|otherwise)',
            r'(failure|refusal)\s+to\s+comply\s+will\s+result\s+in',

            # Phishing indicators
            r'(click|visit|go\s+to)\s+(this|the)\s+(link|URL|website)',
            r'(download|open|execute)\s+(this|the)\s+(attachment|file|document)',
            r'(limited\s+time|expiring|expires\s+soon)',
            r'(act|respond|reply)\s+(now|immediately|within)',

            # Impersonation
            r'(I\s+am|this\s+is)\s+(from|calling\s+from)\s+(IT|HR|security|management)',
            r'(on\s+behalf\s+of|representing)\s+(IT|security|management|CEO|executive)',

            # Financial manipulation
            r'\b(wire\s+transfer|payment|invoice|refund)\b.*?\b(urgent|immediate|today)\b',
            r'(update|change|verify)\s+(payment|banking|payroll)\s+(information|details)',
        ]

    def _init_cybersecurity_patterns(self):
        """Initialize cybersecurity threat patterns"""
        self.cybersecurity_patterns = [
            # Command injection
            r'(\$\(|`|;|\||&&)\s*(bash|sh|cmd|powershell|python|perl)',
            r'(curl|wget|nc|netcat|telnet)\s+-',
            r'(chmod|chown|sudo|su\s+-)',

            # Privilege escalation
            r'(sudo|su\s+root|runas\s+administrator)',
            r'(privilege\s+escalation|elevate\s+privileges)',
            r'(bypass|circumvent)\s+(UAC|authentication|authorization)',

            # Network exploitation
            r'(reverse\s+shell|bind\s+shell|backdoor)',
            r'(exploit|vulnerability|CVE-\d{4}-\d{4,})',
            r'(metasploit|meterpreter|cobalt\s+strike)',

            # Malicious URLs/IPs
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b',
            r'(http|https|ftp)://.*?(exploit|payload|malware)',

            # SQL injection
            r"(';|\";\s*)(\s*--|\s*/\*|\s*union\s+select)",
            r'(drop|delete|truncate)\s+table',
            r'exec(ute)?\s*\(',

            # Path traversal
            r'\.\.(/|\\){2,}',
            r'(file://|/etc/passwd|/etc/shadow|C:\\Windows)',

            # Scripting attacks
            r'<script[^>]*>.*?</script>',
            r'(eval|exec|system|shell_exec)\s*\(',
            r'(document\.cookie|window\.location)',
        ]

    def _init_malware_patterns(self):
        """Initialize malware and exploit indicators"""
        self.malware_patterns = [
            # Malware terms
            r'\b(ransomware|trojan|rootkit|keylogger|spyware)\b',
            r'\b(virus|worm|malware|botnet)\b',
            r'\b(payload|shellcode|exploit\s+kit)\b',

            # Obfuscation
            r'(base64|hex|rot13)\s*(encode|decode)',
            r'eval\(.*?decode',
            r'chr\(\d+\).*?chr\(\d+\)',  # Character code obfuscation

            # Encryption/encoding (suspicious context)
            r'(AES|RSA|encrypt|cipher).*?(key|password|credential)',

            # C2/Exfiltration
            r'(command\s+and\s+control|C2|exfiltrate)',
            r'(beacon|callback|phone\s+home)',
            r'(send|upload|transmit).*?(credentials?|passwords?|data)',

            # File operations
            r'(download|fetch|retrieve).*?(exe|dll|bin|payload)',
            r'(write|create).*?(registry|startup|scheduled\s+task)',
        ]

    def _init_pii_patterns(self):
        """Initialize PII (Personally Identifiable Information) patterns"""
        self.pii_patterns = [
            # SSN
            r'\b\d{3}-\d{2}-\d{4}\b',
            r'\b\d{9}\b',

            # Credit card numbers
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',

            # Email addresses (in suspicious context)
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',

            # Phone numbers
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\b\+\d{1,3}[-.\s]?\d{1,14}\b',

            # Passwords/credentials in clear text
            r'(password|passwd|pwd)\s*[:=]\s*["\']?[A-Za-z0-9!@#$%^&*]{6,}',
            r'(api[_-]?key|token)\s*[:=]\s*["\']?[A-Za-z0-9]{20,}',

            # Medical records
            r'\b(patient\s+id|medical\s+record|diagnosis\s+code)\b',

            # Financial data
            r'\b(account\s+number|routing\s+number|IBAN)\b',
        ]

    def _init_offensive_content_patterns(self):
        """Initialize offensive and inappropriate content patterns"""
        self.offensive_content_patterns = [
            # Hate speech indicators
            r'\b(hate\s+speech|racial\s+slur|ethnic\s+slur)\b',

            # Violence/threats
            r'\b(kill|murder|assassinate|harm|attack)\s+(you|them|associates|employees)\b',
            r'\b(bomb|explosive|weapon|gun)\s+(threat|attack)\b',

            # Harassment
            r'\b(harass|stalk|intimidate|threaten)\b',

            # Inappropriate content
            r'\b(pornographic|explicit\s+sexual|adult\s+content)\b',
        ]

    def _init_policy_violation_patterns(self):
        """Initialize corporate policy violation patterns"""
        self.policy_violation_patterns = [
            # Confidential information
            r'\b(confidential|proprietary|trade\s+secret|internal\s+only)\b',
            r'\b(NDA|non-disclosure|classified)\b',

            # Insider information
            r'\b(insider\s+(trading|information)|material\s+non-public)\b',

            # Discrimination
            r'\b(discriminate|discrimination)\s+(based\s+on|against)',

            # Legal violations
            r'\b(illegal|unlawful|prohibited\s+by\s+law)\b',

            # Data breach
            r'\b(data\s+breach|unauthorized\s+access|stolen\s+data)\b',
        ]

    def verify_document(self, content: str, filename: str = "unknown") -> VerificationResult:
        """
        Perform comprehensive security verification on document content.

        Args:
            content: Document text content
            filename: Original filename for logging

        Returns:
            VerificationResult with threat detection details
        """
        threats: List[ThreatDetection] = []

        # Run all security scans
        threats.extend(self._scan_prompt_injection(content))
        threats.extend(self._scan_social_engineering(content))
        threats.extend(self._scan_cybersecurity_threats(content))
        threats.extend(self._scan_malware_indicators(content))
        threats.extend(self._scan_pii_exposure(content))
        threats.extend(self._scan_offensive_content(content))
        threats.extend(self._scan_policy_violations(content))

        # Optionally use LLM for semantic analysis
        if self.use_llm_verification and threats:
            threats.extend(self._llm_semantic_verification(content, threats))

        # Determine overall severity
        overall_severity = self._calculate_overall_severity(threats)

        # Determine if document is safe
        is_safe = len(threats) == 0 or all(
            t.severity in [ThreatSeverity.NONE, ThreatSeverity.LOW]
            for t in threats
        )

        # Block high/critical threats
        allow_ingestion = is_safe and overall_severity not in [
            ThreatSeverity.HIGH,
            ThreatSeverity.CRITICAL
        ]

        # Generate summary
        summary = self._generate_summary(threats, overall_severity)

        # Generate document hash for audit trail
        import hashlib
        document_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        return VerificationResult(
            is_safe=is_safe,
            threats_detected=threats,
            overall_severity=overall_severity,
            document_hash=document_hash,
            verified_at=datetime.now(),
            summary=summary,
            allow_ingestion=allow_ingestion
        )

    def _scan_prompt_injection(self, content: str) -> List[ThreatDetection]:
        """Scan for prompt injection and model manipulation attempts"""
        threats = []
        content_lower = content.lower()

        for pattern in self.prompt_injection_patterns:
            matches = list(re.finditer(pattern, content_lower, re.IGNORECASE | re.DOTALL))
            for match in matches:
                context = self._extract_context(content, match.start(), match.end())
                threats.append(ThreatDetection(
                    category=ThreatCategory.PROMPT_INJECTION,
                    severity=ThreatSeverity.CRITICAL,
                    pattern=pattern,
                    context=context,
                    confidence=0.95,
                    recommendation="Block document. Contains prompt injection attempt."
                ))

        return threats

    def _scan_social_engineering(self, content: str) -> List[ThreatDetection]:
        """Scan for social engineering and phishing attempts"""
        threats = []

        for pattern in self.social_engineering_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                context = self._extract_context(content, match.start(), match.end())

                # Determine severity based on pattern type
                severity = ThreatSeverity.HIGH
                if 'credential' in pattern or 'password' in pattern:
                    severity = ThreatSeverity.CRITICAL
                elif 'urgent' in pattern or 'immediate' in pattern:
                    severity = ThreatSeverity.HIGH
                else:
                    severity = ThreatSeverity.MEDIUM

                threats.append(ThreatDetection(
                    category=ThreatCategory.SOCIAL_ENGINEERING,
                    severity=severity,
                    pattern=pattern,
                    context=context,
                    confidence=0.85,
                    recommendation="Review document. Contains social engineering indicators."
                ))

        return threats

    def _scan_cybersecurity_threats(self, content: str) -> List[ThreatDetection]:
        """Scan for cybersecurity threats and exploits"""
        threats = []

        for pattern in self.cybersecurity_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                context = self._extract_context(content, match.start(), match.end())
                threats.append(ThreatDetection(
                    category=ThreatCategory.CYBERSECURITY_THREAT,
                    severity=ThreatSeverity.CRITICAL,
                    pattern=pattern,
                    context=context,
                    confidence=0.90,
                    recommendation="Block document. Contains cybersecurity threat indicators."
                ))

        return threats

    def _scan_malware_indicators(self, content: str) -> List[ThreatDetection]:
        """Scan for malware indicators"""
        threats = []

        for pattern in self.malware_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                context = self._extract_context(content, match.start(), match.end())
                threats.append(ThreatDetection(
                    category=ThreatCategory.MALWARE_INDICATORS,
                    severity=ThreatSeverity.HIGH,
                    pattern=pattern,
                    context=context,
                    confidence=0.80,
                    recommendation="Block document. Contains malware indicators."
                ))

        return threats

    def _scan_pii_exposure(self, content: str) -> List[ThreatDetection]:
        """Scan for PII exposure risks"""
        threats = []

        for pattern in self.pii_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                context = self._extract_context(content, match.start(), match.end(), mask_pii=True)
                threats.append(ThreatDetection(
                    category=ThreatCategory.PII_EXPOSURE,
                    severity=ThreatSeverity.HIGH,
                    pattern=pattern,
                    context=context,
                    confidence=0.75,
                    recommendation="Review document. May contain PII that should not be indexed."
                ))

        return threats

    def _scan_offensive_content(self, content: str) -> List[ThreatDetection]:
        """Scan for offensive or inappropriate content"""
        threats = []

        for pattern in self.offensive_content_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                context = self._extract_context(content, match.start(), match.end())
                threats.append(ThreatDetection(
                    category=ThreatCategory.OFFENSIVE_CONTENT,
                    severity=ThreatSeverity.MEDIUM,
                    pattern=pattern,
                    context=context,
                    confidence=0.70,
                    recommendation="Review document. May contain inappropriate content."
                ))

        return threats

    def _scan_policy_violations(self, content: str) -> List[ThreatDetection]:
        """Scan for corporate policy violations"""
        threats = []

        for pattern in self.policy_violation_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                context = self._extract_context(content, match.start(), match.end())
                threats.append(ThreatDetection(
                    category=ThreatCategory.POLICY_VIOLATION,
                    severity=ThreatSeverity.MEDIUM,
                    pattern=pattern,
                    context=context,
                    confidence=0.65,
                    recommendation="Review document for policy compliance."
                ))

        return threats

    def _llm_semantic_verification(self, content: str, existing_threats: List[ThreatDetection]) -> List[ThreatDetection]:
        """Use LLM for semantic threat analysis (optional)"""
        # Placeholder for LLM-based verification
        # Would use Vertex AI to analyze semantic threats
        return []

    def _extract_context(self, content: str, start: int, end: int, window: int = 50, mask_pii: bool = False) -> str:
        """Extract context around a match"""
        context_start = max(0, start - window)
        context_end = min(len(content), end + window)
        context = content[context_start:context_end]

        if mask_pii:
            context = re.sub(r'\d{3}-\d{2}-\d{4}', 'XXX-XX-XXXX', context)
            context = re.sub(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', 'XXXX-XXXX-XXXX-XXXX', context)

        return context.strip()

    def _calculate_overall_severity(self, threats: List[ThreatDetection]) -> ThreatSeverity:
        """Calculate overall severity from all threats"""
        if not threats:
            return ThreatSeverity.NONE

        severity_scores = {
            ThreatSeverity.NONE: 0,
            ThreatSeverity.LOW: 1,
            ThreatSeverity.MEDIUM: 2,
            ThreatSeverity.HIGH: 3,
            ThreatSeverity.CRITICAL: 4
        }

        max_severity = max(severity_scores[t.severity] for t in threats)

        for severity, score in severity_scores.items():
            if score == max_severity:
                return severity

        return ThreatSeverity.NONE

    def _generate_summary(self, threats: List[ThreatDetection], overall_severity: ThreatSeverity) -> str:
        """Generate human-readable summary of verification"""
        if not threats:
            return "Document passed all security checks. Safe for ingestion."

        threat_counts = {}
        for threat in threats:
            cat = threat.category.value
            threat_counts[cat] = threat_counts.get(cat, 0) + 1

        summary_parts = [
            f"Document verification: {overall_severity.value.upper()} severity",
            f"Detected {len(threats)} potential threat(s):"
        ]

        for cat, count in threat_counts.items():
            summary_parts.append(f"  - {cat}: {count}")

        if overall_severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]:
            summary_parts.append("Recommendation: BLOCK document from ingestion.")
        elif overall_severity == ThreatSeverity.MEDIUM:
            summary_parts.append("Recommendation: REVIEW document before ingestion.")
        else:
            summary_parts.append("Recommendation: Document may proceed with caution.")

        return "\n".join(summary_parts)
