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
from uuid import uuid4
import os
from typing import Optional

PROJECT_ID = os.getenv("PROJECT_ID", "mtech-stores-sre-monit-dev")

app = FastAPI(
    title="Macy Rag Storebot",
    description="RAG-powered retail knowledge assistant API with Safety Framework",
    version="1.0.0"
)
rag = RAGOrchestrator(project_id=PROJECT_ID)
feedback_store = FeedbackStore()

# Initialize Safety Framework
safety_classifier = SafetyClassifier(project_id=PROJECT_ID, use_llm_classification=True)
safety_policy = SafetyPolicyEngine()
safety_reporting = ConfidentialReportingService(project_id=PROJECT_ID)

class Query(BaseModel):
    question: str
    store_id: str | None = None
    user_id: str | None = None  # For safety reporting
    device_id: str | None = None  # For safety reporting
    session_id: str | None = None  # For safety reporting

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
    """Health check endpoint for App Engine"""
    return {"status": "healthy", "project_id": PROJECT_ID}

@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...), store_id: str = Form(...)):
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    real_name = file.filename
    suffix = Path(real_name).suffix
    save_path = raw_dir / f"{uuid4().hex}{suffix}"

    content = await file.read()
    save_path.write_bytes(content)

    processor = DocumentProcessor(save_path)
    text = list(processor.document_dict.values())[0]

    chunks = rag.chunker.semantic_chunker(text)
    embeddings = rag.embedder.embed(chunks)

    metadatas = [{
        "source": real_name,     # <-- original filename preserved
        "store_id": store_id,
        "doc_type": "kb_article"
    } for _ in chunks]

    rag.vector_store.add(chunks, embeddings, metadatas)
    rag.bm25.add(chunks, metadatas)

    return {"status": "indexed", "chunks": len(chunks), "source": real_name}

@app.post("/ask")
def ask_question(query: Query):
    """
    Ask a question to the RAG system with integrated safety checks.

    Flow:
    1. Safety Classification - Check for harmful content
    2. Policy Response - Generate appropriate response if safety issue detected
    3. Escalation - Submit confidential report if needed
    4. RAG Processing - If safe, proceed with normal question answering

    Returns:
        - For safe questions: Standard RAG response
        - For safety issues: Supportive message with resources
    """
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

        # Return safety response instead of RAG answer
        return {
            "answer": response_message,
            "safety_classification": classification.category.value,
            "severity": classification.severity.value,
            "support_resources": safety_response.support_resources,
            "allow_continuation": safety_response.allow_continuation,
            "is_safety_response": True
        }

    # STEP 4: If safe, proceed with normal RAG processing
    # Only questions classified as SAFE_OPERATIONAL reach this point
    rag_response = rag.ask(query.question)

    # Add safety metadata to response
    rag_response["safety_classification"] = "safe_operational"
    rag_response["is_safety_response"] = False

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
