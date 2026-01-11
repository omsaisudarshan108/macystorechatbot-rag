"""
Document Security & Verification Module

Implements comprehensive safety gates for document ingestion to prevent:
- AI poisoning and prompt injection
- Social engineering attacks
- Malware and exploit propagation
- OWASP LLM Top 10 violations
- Privacy and compliance breaches
"""

from .document_verifier import (
    DocumentVerifier,
    VerificationResult,
    ThreatCategory,
    ThreatSeverity
)

__all__ = [
    'DocumentVerifier',
    'VerificationResult',
    'ThreatCategory',
    'ThreatSeverity'
]
