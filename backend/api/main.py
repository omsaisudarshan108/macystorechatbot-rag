from fastapi import UploadFile, File, Form
from pathlib import Path
from backend.ingestion.loaders import DocumentProcessor
from backend.ingestion.chunkers import Chunker
from fastapi import FastAPI
from pydantic import BaseModel
from backend.rag.orchestrator import RAGOrchestrator
from backend.feedback import FeedbackStore
from backend.safety import (
    SafetyClassifier,
    SafetyPolicyEngine,
    ConfidentialReportingService,
    SafetyCategory
)
from backend.safety.response_filter import ResponseSafetyFilter, SafetyAction
from backend.security import InfrastructureSecurityGuard
from backend.document_security import DocumentVerifier, ThreatSeverity
from backend.i18n import LanguageDetector, TranslationService
from uuid import uuid4
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "mtech-stores-sre-monit-dev")

app = FastAPI(
    title="Macy Rag Storebot",
    description="RAG-powered retail knowledge assistant API with Safety Framework and Document Verification",
    version="1.0.0"
)
rag = RAGOrchestrator(project_id=PROJECT_ID)
feedback_store = FeedbackStore()

# Initialize Safety Framework
safety_classifier = SafetyClassifier(project_id=PROJECT_ID, use_llm_classification=True)
safety_policy = SafetyPolicyEngine()
safety_reporting = ConfidentialReportingService(project_id=PROJECT_ID)

# Initialize Infrastructure Security
infrastructure_guard = InfrastructureSecurityGuard()

# Initialize Document Security
document_verifier = DocumentVerifier(use_llm_verification=False, project_id=PROJECT_ID)

# Initialize Response Safety Filter
response_filter = ResponseSafetyFilter()

# Initialize i18n Services
language_detector = LanguageDetector()
translation_service = TranslationService()

class Query(BaseModel):
    question: str
    store_id: str | None = None
    user_id: str | None = None  # For safety reporting
    device_id: str | None = None  # For safety reporting
    session_id: str | None = None  # For safety reporting
    language: str | None = None  # Optional language override

class FeedbackSubmission(BaseModel):
    question: str
    answer: str
    rating: int  # 1-5 stars
    was_helpful: bool
    comment: Optional[str] = None
    store_id: Optional[str] = None
    session_id: Optional[str] = None

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Macy RAG Storebot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "ingest": "/ingest",
            "ask": "/ask",
            "feedback": "/feedback",
            "feedback_stats": "/feedback/stats"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "local"),
        "safety_features": {
            "document_verification": True,
            "prompt_injection_protection": True,
            "owasp_llm_guardrails": True,
            "response_safety_filter": True,
            "confidential_escalation": True
        }
    }

@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...), store_id: str = Form(...)):
    """
    Ingest document with comprehensive security verification.

    Security Gates:
    1. Document verification (malware, prompt injection, social engineering)
    2. Content safety validation
    3. Policy compliance check

    Only verified documents are chunked, embedded, and stored.
    """
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    real_name = file.filename
    suffix = Path(real_name).suffix
    save_path = raw_dir / f"{uuid4().hex}{suffix}"

    content = await file.read()
    save_path.write_bytes(content)

    try:
        # STEP 1: Extract text from document
        processor = DocumentProcessor(save_path)
        text = list(processor.document_dict.values())[0]

        # STEP 2: SECURITY GATE - Document Verification
        logger.info(f"Verifying document: {real_name}")
        verification_result = document_verifier.verify_document(text, real_name)

        # STEP 3: Check verification result
        if not verification_result.allow_ingestion:
            logger.warning(
                f"Document blocked: {real_name} | "
                f"Severity: {verification_result.overall_severity.value} | "
                f"Threats: {len(verification_result.threats_detected)}"
            )

            # Log threat details for security audit
            for threat in verification_result.threats_detected:
                logger.warning(
                    f"  - {threat.category.value}: {threat.severity.value} "
                    f"(confidence: {threat.confidence:.2f})"
                )

            return {
                "status": "blocked",
                "reason": "security_threat_detected",
                "severity": verification_result.overall_severity.value,
                "summary": verification_result.summary,
                "threats_count": len(verification_result.threats_detected),
                "document_hash": verification_result.document_hash,
                "message": "Document contains security threats and cannot be ingested. "
                          "Please review the content and remove any malicious patterns, "
                          "prompt injections, or policy violations."
            }

        # STEP 4: Log warnings for medium severity (allow but flag)
        if verification_result.overall_severity == ThreatSeverity.MEDIUM:
            logger.info(
                f"Document ingested with warnings: {real_name} | "
                f"Threats: {len(verification_result.threats_detected)}"
            )

        # STEP 5: Proceed with ingestion if verified safe
        logger.info(f"Document verified safe: {real_name}")

        chunks = rag.chunker.semantic_chunker(text)
        embeddings = rag.embedder.embed(chunks)

        metadatas = [{
            "source": real_name,
            "store_id": store_id,
            "doc_type": "kb_article",
            "verified": True,
            "verification_hash": verification_result.document_hash,
            "verified_at": verification_result.verified_at.isoformat()
        } for _ in chunks]

        rag.vector_store.add(chunks, embeddings, metadatas)
        rag.bm25.add(chunks, metadatas)

        result = {
            "status": "indexed",
            "chunks": len(chunks),
            "source": real_name,
            "verification": {
                "passed": True,
                "severity": verification_result.overall_severity.value,
                "document_hash": verification_result.document_hash
            }
        }

        # Add warnings if any low/medium threats detected
        if verification_result.threats_detected:
            result["warnings"] = [
                {
                    "category": t.category.value,
                    "severity": t.severity.value,
                    "recommendation": t.recommendation
                }
                for t in verification_result.threats_detected
            ]

        return result

    except Exception as e:
        logger.error(f"Error processing document {real_name}: {str(e)}")
        raise

@app.post("/ask")
def ask_question(query: Query):
    """
    Ask a question to the RAG system with integrated safety, security, and i18n.

    Flow:
    0. Language Detection - Auto-detect language from input
    1. Infrastructure Security Check - Prevent disclosure of backend details
    2. Safety Classification - Check for harmful content
    3. Policy Response - Generate appropriate response if safety issue detected
    4. Escalation - Submit confidential report if needed
    5. RAG Processing - If safe, proceed with normal question answering
    6. Response Translation - Return response in detected language

    Returns:
        - For infrastructure queries: Standard compliant response (localized)
        - For safe questions: Standard RAG response (localized)
        - For safety issues: Supportive message with resources (localized)
    """
    # STEP 0: Language Detection
    # Auto-detect language from user input (English or Spanish)
    if query.language:
        # Use provided language if specified
        detected_language = language_detector.detect_language_code(query.language)
    else:
        # Auto-detect from question text
        detected_language = language_detector.detect_language_code(query.question)

    # Log language detection
    logger.info(f"Language detected: {detected_language} for question: {query.question[:50]}...")

    # STEP 1: Infrastructure Security Check
    # Block attempts to extract backend infrastructure information
    if infrastructure_guard.should_block(query.question):
        # Return infrastructure response in detected language
        infra_response = infrastructure_guard.get_standard_response()
        # TODO: Translate infrastructure response if needed
        return {
            "answer": infra_response,
            "citations": [],
            "is_infrastructure_blocked": True,
            "safety_classification": "safe_operational",
            "is_safety_response": False,
            "language": detected_language,
            "language_name": translation_service.get_language_name(detected_language)
        }

    # STEP 1: Safety Classification
    # Check message for safety concerns BEFORE processing with RAG
    context = {
        'store_id': query.store_id,
        'device_id': query.device_id,
        'session_id': query.session_id,
        'user_id': query.user_id
    }

    classification = safety_classifier.classify(query.question, context=context)

    # STEP 2: Check if this is a safety concern
    if classification.category != SafetyCategory.SAFE_OPERATIONAL:
        # Generate appropriate safety response
        safety_response = safety_policy.generate_response(classification)

        # STEP 3: Escalate if needed
        if safety_response.requires_escalation:
            # Submit confidential report
            report_id = safety_reporting.submit_report(
                user_id=query.user_id or "anonymous",
                message=query.question,
                classification={
                    'category': classification.category.value,
                    'severity': classification.severity.value,
                    'confidence': classification.confidence,
                    'detected_patterns': classification.detected_patterns,
                    'reasoning': classification.reasoning
                },
                policy_response={
                    'requires_escalation': safety_response.requires_escalation,
                    'escalation_priority': safety_response.escalation_priority,
                    'recipients': safety_response.recipients
                },
                context=context
            )

            # Add report ID to response
            response_message = safety_response.message + f"\n\n*Reference: {report_id}*"
        else:
            response_message = safety_response.message

        # Return safety response instead of RAG answer (localized)
        return {
            "answer": response_message,
            "safety_classification": classification.category.value,
            "severity": classification.severity.value,
            "support_resources": safety_response.support_resources,
            "allow_continuation": safety_response.allow_continuation,
            "is_safety_response": True,
            "language": detected_language,
            "language_name": translation_service.get_language_name(detected_language)
        }

    # STEP 4: If safe, proceed with normal RAG processing
    # Only questions classified as SAFE_OPERATIONAL reach this point
    rag_response = rag.ask(query.question)

    # STEP 5: Response Safety Filter (Post-Generation)
    # Check generated response for hallucination and safety violations
    context_docs = [doc.get("text", "") for doc in rag_response.get("context", [])]

    safety_check = response_filter.check_response_safety(
        response=rag_response.get("answer", ""),
        context_docs=context_docs,
        question=query.question
    )

    # STEP 6: Apply safety filter action
    if safety_check.action == SafetyAction.BLOCK:
        # Translate blocked message
        blocked_message = translation_service.get("response_safety.insufficient_info", detected_language)
        return {
            "answer": blocked_message,
            "citations": [],
            "safety_classification": "safe_operational",
            "is_safety_response": False,
            "response_safety": {
                "status": "blocked",
                "action": "blocked",
                "reason": translation_service.get("response_safety.blocked_reason", detected_language),
                "confidence": safety_check.confidence
            },
            "language": detected_language,
            "language_name": translation_service.get_language_name(detected_language)
        }
    elif safety_check.action == SafetyAction.MODIFY:
        rag_response["answer"] = safety_check.safe_response
        rag_response["response_safety"] = {
            "status": "modified",
            "action": "modified",
            "reason": translation_service.get("response_safety.modified_reason", detected_language),
            "confidence": safety_check.confidence
        }
    else:
        rag_response["response_safety"] = {
            "status": "passed",
            "action": "pass",
            "reason": translation_service.get("response_safety.passed_reason", detected_language),
            "confidence": safety_check.confidence
        }

    # Add safety metadata and language to response
    rag_response["safety_classification"] = "safe_operational"
    rag_response["is_safety_response"] = False
    rag_response["language"] = detected_language
    rag_response["language_name"] = translation_service.get_language_name(detected_language)

    return rag_response

@app.post("/feedback")
def submit_feedback(feedback: FeedbackSubmission):
    """
    Submit feedback about an answer.

    Store associates can rate answers and provide feedback on helpfulness.
    """
    try:
        result = feedback_store.save_feedback(
            question=feedback.question,
            answer=feedback.answer,
            rating=feedback.rating,
            was_helpful=feedback.was_helpful,
            comment=feedback.comment,
            store_id=feedback.store_id,
            session_id=feedback.session_id
        )
        return {
            "status": "success",
            "message": "Thank you for your feedback!",
            "feedback_id": result["id"]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save feedback: {str(e)}"
        }

@app.get("/feedback/stats")
def get_feedback_stats():
    """
    Get statistics about collected feedback.

    Returns aggregate metrics like average rating, helpfulness percentage, etc.
    """
    try:
        stats = feedback_store.get_feedback_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve stats: {str(e)}"
        }
