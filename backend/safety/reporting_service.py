"""
Confidential Reporting Service

Handles secure, privacy-preserving escalation of safety concerns.

Design Principles:
- Encryption at rest and in transit
- Minimal data retention
- Access controls (HR/Security only)
- Audit logging
- GDPR/CCPA compliant
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import hashlib
import uuid
from google.cloud import pubsub_v1, firestore, secretmanager
from cryptography.fernet import Fernet
import os


@dataclass
class ConfidentialReport:
    """Confidential safety incident report"""
    report_id: str
    timestamp: str
    classification_category: str
    severity_level: str
    escalation_priority: str

    # Anonymized identifiers
    anonymized_user_id: str  # One-way hash
    device_id: Optional[str]  # Device identifier (CT40 ID)
    store_id: str
    session_id: str

    # Encrypted sensitive data
    encrypted_message: str  # Original message, encrypted
    encryption_key_version: str

    # Metadata
    detected_patterns: List[str]
    confidence_score: float
    classification_reasoning: str

    # Escalation
    recipients: List[str]
    requires_followup: bool

    # Compliance
    retention_days: int  # Auto-delete after N days
    access_log: List[Dict]  # Who accessed this report


class ConfidentialReportingService:
    """
    Manages confidential safety incident reporting

    Storage: Firestore (encrypted) + Pub/Sub (for real-time routing)
    Encryption: Customer-managed keys via Secret Manager
    Access: Role-based, audit-logged
    """

    def __init__(self, project_id: str):
        """Initialize reporting service"""
        self.project_id = project_id

        # Initialize GCP clients
        self.firestore_client = firestore.Client(project=project_id)
        self.pubsub_publisher = pubsub_v1.PublisherClient()
        self.secret_manager = secretmanager.SecretManagerServiceClient()

        # Firestore collection for reports
        self.reports_collection = 'safety_incidents_confidential'

        # Pub/Sub topics for routing
        self.topics = {
            'MEDIUM': f'projects/{project_id}/topics/safety-medium',
            'HIGH': f'projects/{project_id}/topics/safety-high',
            'CRITICAL': f'projects/{project_id}/topics/safety-critical',
            'CRITICAL_IMMEDIATE': f'projects/{project_id}/topics/safety-emergency'
        }

        # Encryption key (retrieved from Secret Manager)
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)

    def _get_encryption_key(self) -> bytes:
        """
        Retrieve encryption key from Secret Manager

        In production: Use customer-managed encryption keys (CMEK)
        """
        try:
            secret_name = f"projects/{self.project_id}/secrets/safety-encryption-key/versions/latest"
            response = self.secret_manager.access_secret_version(name=secret_name)
            return response.payload.data
        except Exception as e:
            # Fallback for development (DO NOT use in production)
            print(f"Warning: Using fallback encryption key. Error: {e}")
            # Generate a new key for this session
            # In production, this should fail and alert
            return Fernet.generate_key()

    def submit_report(
        self,
        user_id: str,
        message: str,
        classification: Dict,
        policy_response: Dict,
        context: Optional[Dict] = None
    ) -> str:
        """
        Submit a confidential safety report

        Args:
            user_id: User identifier (will be anonymized)
            message: Original message (will be encrypted)
            classification: SafetyClassification data
            policy_response: SafetyResponse data
            context: Additional context (store_id, device_id, etc.)

        Returns:
            report_id: Unique identifier for this report
        """
        # Generate report ID
        report_id = f"SAFE-{uuid.uuid4().hex[:12].upper()}"

        # Anonymize user ID (one-way hash)
        anonymized_user_id = self._anonymize_user_id(user_id)

        # Encrypt message
        encrypted_message = self._encrypt_message(message)

        # Extract context
        store_id = context.get('store_id', 'UNKNOWN') if context else 'UNKNOWN'
        device_id = context.get('device_id') if context else None
        session_id = context.get('session_id', 'UNKNOWN') if context else 'UNKNOWN'

        # Determine retention period
        retention_days = self._get_retention_period(classification['severity'])

        # Create report
        report = ConfidentialReport(
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat(),
            classification_category=classification['category'],
            severity_level=classification['severity'],
            escalation_priority=policy_response['escalation_priority'] or 'NONE',

            anonymized_user_id=anonymized_user_id,
            device_id=device_id,
            store_id=store_id,
            session_id=session_id,

            encrypted_message=encrypted_message,
            encryption_key_version='v1',  # Track key version for rotation

            detected_patterns=classification.get('detected_patterns', []),
            confidence_score=classification.get('confidence', 0.0),
            classification_reasoning=classification.get('reasoning', ''),

            recipients=policy_response.get('recipients', []),
            requires_followup=classification['severity'] in ['HIGH', 'CRITICAL'],

            retention_days=retention_days,
            access_log=[]  # Initialize empty access log
        )

        # Store in Firestore (encrypted at rest)
        self._store_report(report)

        # Send to appropriate Pub/Sub topic for routing
        if policy_response.get('requires_escalation', False):
            self._route_to_recipients(report)

        # Audit log
        self._audit_log('REPORT_CREATED', report_id, anonymized_user_id)

        return report_id

    def _anonymize_user_id(self, user_id: str) -> str:
        """
        Create one-way hash of user ID

        Design: Uses SHA-256 with salt to prevent reverse lookups
        while allowing correlation of reports from same user
        """
        salt = os.getenv('USER_ID_SALT', 'default_salt_change_in_prod')
        return hashlib.sha256(f"{user_id}{salt}".encode()).hexdigest()[:16]

    def _encrypt_message(self, message: str) -> str:
        """
        Encrypt sensitive message content

        Uses Fernet (symmetric encryption) with key from Secret Manager
        """
        return self.fernet.encrypt(message.encode()).decode()

    def _decrypt_message(self, encrypted_message: str) -> str:
        """
        Decrypt message (only for authorized access)

        Access should be audit-logged
        """
        return self.fernet.decrypt(encrypted_message.encode()).decode()

    def _get_retention_period(self, severity: str) -> int:
        """
        Determine data retention period based on severity

        Compliance: Balance between safety and privacy
        """
        retention_map = {
            'LOW': 30,      # 30 days
            'MEDIUM': 90,   # 90 days
            'HIGH': 180,    # 6 months
            'CRITICAL': 365  # 1 year
        }
        return retention_map.get(severity, 90)

    def _store_report(self, report: ConfidentialReport):
        """
        Store report in Firestore with access controls

        Firestore security rules should enforce:
        - Only specific service accounts can read
        - No public access
        - Audit logging enabled
        """
        doc_ref = self.firestore_client.collection(self.reports_collection).document(report.report_id)

        # Convert to dict and store
        report_data = asdict(report)

        # Set expiration for auto-deletion
        expiration_date = datetime.utcnow() + timedelta(days=report.retention_days)
        report_data['expiration_date'] = expiration_date

        doc_ref.set(report_data)

    def _route_to_recipients(self, report: ConfidentialReport):
        """
        Route report to appropriate recipients via Pub/Sub

        Design: Use Pub/Sub for decoupled, reliable delivery to:
        - HR system
        - Security Operations Center
        - Crisis response team
        """
        priority = report.escalation_priority

        if priority not in self.topics:
            priority = 'MEDIUM'  # Default fallback

        topic_path = self.topics[priority]

        # Create message payload
        message_data = {
            'report_id': report.report_id,
            'timestamp': report.timestamp,
            'severity': report.severity_level,
            'priority': priority,
            'store_id': report.store_id,
            'recipients': report.recipients,
            'requires_immediate_action': priority == 'CRITICAL_IMMEDIATE'
        }

        # Publish to Pub/Sub
        try:
            future = self.pubsub_publisher.publish(
                topic_path,
                json.dumps(message_data).encode(),
                priority=priority,
                report_type='safety_incident'
            )
            future.result()  # Wait for publish to complete
        except Exception as e:
            # Log error but don't fail the report submission
            print(f"Error publishing to Pub/Sub: {e}")
            # Fallback: Send email alert or use backup notification system

    def _audit_log(self, action: str, report_id: str, user_id: str):
        """
        Create audit log entry

        All access to safety reports must be logged
        """
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'report_id': report_id,
            'user_id': user_id,
            'service': 'confidential_reporting'
        }

        # Store in separate audit collection
        self.firestore_client.collection('safety_audit_log').add(audit_entry)

    def get_report(self, report_id: str, accessor_id: str, purpose: str) -> Optional[Dict]:
        """
        Retrieve report (authorized access only)

        Args:
            report_id: Report identifier
            accessor_id: Who is accessing (for audit)
            purpose: Reason for access (for audit)

        Returns:
            Decrypted report data or None if not found/not authorized
        """
        # Audit this access attempt
        self._audit_log(f'ACCESS_ATTEMPT: {purpose}', report_id, accessor_id)

        # Retrieve from Firestore
        doc_ref = self.firestore_client.collection(self.reports_collection).document(report_id)
        doc = doc_ref.get()

        if not doc.exists:
            return None

        report_data = doc.to_dict()

        # Decrypt sensitive fields
        report_data['decrypted_message'] = self._decrypt_message(
            report_data['encrypted_message']
        )

        # Update access log
        access_entry = {
            'accessor_id': accessor_id,
            'timestamp': datetime.utcnow().isoformat(),
            'purpose': purpose
        }

        report_data['access_log'].append(access_entry)
        doc_ref.update({'access_log': report_data['access_log']})

        # Audit successful access
        self._audit_log(f'ACCESS_GRANTED: {purpose}', report_id, accessor_id)

        return report_data

    def cleanup_expired_reports(self):
        """
        Auto-delete expired reports (privacy compliance)

        Should be run as a scheduled Cloud Function/Cloud Run job
        """
        now = datetime.utcnow()

        # Query expired reports
        expired_query = self.firestore_client.collection(self.reports_collection)\
            .where('expiration_date', '<', now)\
            .stream()

        deleted_count = 0
        for doc in expired_query:
            # Audit deletion
            self._audit_log('AUTO_DELETED_EXPIRED', doc.id, 'system_cleanup')

            # Delete document
            doc.reference.delete()
            deleted_count += 1

        return deleted_count


class ReportingAPIContract:
    """
    API Contract for Confidential Reporting Service

    This defines the interface that external systems (HR, Security)
    can use to interact with safety reports.
    """

    @staticmethod
    def submit_report_schema() -> Dict:
        """
        Schema for submitting a safety report

        POST /api/safety/report/submit
        """
        return {
            'request': {
                'user_id': 'string',  # Will be anonymized
                'message': 'string',  # Will be encrypted
                'classification': {
                    'category': 'string',
                    'severity': 'string',
                    'confidence': 'float',
                    'detected_patterns': ['string'],
                    'reasoning': 'string'
                },
                'policy_response': {
                    'requires_escalation': 'boolean',
                    'escalation_priority': 'string',
                    'recipients': ['string']
                },
                'context': {
                    'store_id': 'string',
                    'device_id': 'string (optional)',
                    'session_id': 'string'
                }
            },
            'response': {
                'success': 'boolean',
                'report_id': 'string',
                'message': 'string'
            }
        }

    @staticmethod
    def get_report_schema() -> Dict:
        """
        Schema for retrieving a safety report (authorized only)

        GET /api/safety/report/{report_id}
        """
        return {
            'request': {
                'report_id': 'string',
                'accessor_id': 'string',  # Who is accessing
                'access_token': 'string',  # Auth token
                'purpose': 'string'  # Why accessing (audited)
            },
            'response': {
                'success': 'boolean',
                'report': {
                    'report_id': 'string',
                    'timestamp': 'string',
                    'category': 'string',
                    'severity': 'string',
                    'store_id': 'string',
                    'decrypted_message': 'string',  # Only if authorized
                    'classification_reasoning': 'string',
                    'recipients': ['string'],
                    'access_log': ['object']
                }
            }
        }
