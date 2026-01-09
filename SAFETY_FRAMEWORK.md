# Safety & Escalation Framework Documentation

## Overview

The Safety & Escalation Framework is a comprehensive system for detecting, responding to, and escalating sensitive content in the Store Associate Chatbot. It prioritizes user safety, dignity, and privacy while ensuring appropriate support resources are provided.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Safety Categories](#safety-categories)
3. [Components](#components)
4. [Integration Flow](#integration-flow)
5. [Response Examples](#response-examples)
6. [Privacy & Compliance](#privacy--compliance)
7. [Configuration](#configuration)
8. [Testing](#testing)
9. [Monitoring & Reporting](#monitoring--reporting)

---

## Architecture Overview

The Safety Framework operates as a **pre-filter** before RAG processing:

```
User Message
    ↓
Safety Classifier (Pattern + LLM)
    ↓
Safety Category + Severity
    ↓
Policy Engine
    ↓
├─ SAFE → Proceed to RAG
├─ LOW RISK → Supportive message + Continue
├─ MEDIUM RISK → Resources + Optional escalation
├─ HIGH RISK → Resources + Escalation + Limited continuation
└─ CRITICAL → Immediate resources + Escalation + Block continuation
```

### Key Design Principles

1. **Privacy-Preserving**: User IDs anonymized, messages encrypted
2. **Non-Judgmental**: Supportive, dignity-preserving language
3. **Conservative Classification**: Err on side of safety
4. **Multi-Layered Detection**: Pattern matching + LLM semantic analysis
5. **Immediate Action**: Critical cases trigger immediate escalation
6. **Compliance-Ready**: GDPR/CCPA compliant data handling

---

## Safety Categories

### 1. SAFE_OPERATIONAL
**Normal work-related questions**

Examples:
- "What is the return policy?"
- "How do I process an exchange?"
- "Where is SKU 12345 in inventory?"

**Response**: Standard RAG processing

---

### 2. PROFANITY_ONLY
**Language includes profanity but no other safety concerns**

**Severity Levels**:
- **LOW**: Mild profanity (damn, hell)
- **MEDIUM**: Moderate profanity
- **HIGH**: Severe profanity or abusive language

**Response**:
- Professional reminder
- EAP resources offered
- Conversation continues

**Example**:
```
User: "This fucking scanner doesn't work"

Response: "I understand you may be frustrated. I'm here to help find solutions.

Let's keep our conversation professional so I can better assist you.

If you're experiencing workplace stress, the Employee Assistance Program
is available at 1-800-XXX-XXXX (confidential support).

How can I help you with the scanner issue?"
```

---

### 3. EMOTIONAL_DISTRESS
**Signs of stress, anxiety, or emotional difficulty**

**Severity Levels**:
- **LOW**: Minor stress ("having a bad day")
- **MEDIUM**: Significant stress ("feeling overwhelmed")
- **HIGH**: Severe distress ("can't function", "panic attack")

**Response**:
- Supportive acknowledgment
- EAP resources
- Option to continue with work questions
- Medium/High: Escalation to HR

**Example**:
```
User: "I'm so stressed I can't function anymore"

Response: "It sounds like you're dealing with something difficult. Support is available.

**Resources to Help:**
• Employee Assistance Program: 1-800-XXX-XXXX (confidential, 24/7)
• 988 Suicide & Crisis Lifeline: Call or text 988
• Speak with your Store Manager (in confidence)

**You're Not Alone:**
Many people go through difficult times. Reaching out for support is a positive step.

Can I also help you with any work-related questions?"
```

---

### 4. SELF_HARM_RISK
**Indications of self-harm ideation or suicidal thoughts**

**Severity Levels**:
- **MEDIUM**: Indirect ("wish I wasn't here")
- **HIGH**: Direct ideation ("want to die")
- **CRITICAL**: Explicit intent or plan ("going to kill myself")

**Response**:
- **Immediate crisis resources** (988, EAP)
- **Escalation to mental health team**
- **No judgment, supportive tone**
- **Continuation blocked for CRITICAL**

**Critical Response Example**:
```
User: "I want to kill myself, I can't do this anymore"

Response: "Your safety is the most important thing right now.

**Immediate Support Available:**
• 988 Suicide & Crisis Lifeline: Call or text 988 (24/7)
• Employee Assistance Program: 1-800-XXX-XXXX (24/7, confidential)
• If this is a medical emergency, call 911

**You Are Not Alone:**
These feelings are temporary, and support is available. Speaking with
a trained professional can help.

**Confidential & Private:**
Your privacy is protected. These resources are confidential and separate
from your employment record.

I care about your wellbeing and want to ensure you get the support you deserve.

*Reference: SAFE-A3F92E1BC45D*"
```

**Escalation**:
- **Priority**: CRITICAL_IMMEDIATE
- **Recipients**: HR, Mental Health Team, Store Manager
- **Report**: Encrypted, access-controlled, audit-logged

---

### 5. HARM_TO_OTHERS_RISK
**Threats or intentions to harm others**

**Severity Levels**:
- **MEDIUM**: Vague frustration ("so angry at them")
- **HIGH**: Specific threats ("want to hurt my manager")
- **CRITICAL**: Imminent threat or weapon mention

**Response**:
- **Immediate security contact**
- **Store manager notification**
- **EAP resources**
- **Escalation to security team**

**Critical Response Example**:
```
User: "I'm going to bring a weapon to work tomorrow"

Response: "**Immediate Action Required**

For everyone's safety, please contact:
• Store Security: Ext. 999
• Call 911 if there is immediate danger
• Store Manager: Available now

**Workplace Safety:**
We take all safety concerns seriously. Speaking with security or
management helps ensure everyone stays safe.

**Confidential Support:**
If you're feeling angry or upset, our Employee Assistance Program
is available 24/7 at 1-800-XXX-XXXX.

*Reference: SAFE-B7E84F2AD91C*"
```

**Escalation**:
- **Priority**: CRITICAL_IMMEDIATE
- **Recipients**: Security, Store Manager, HR, Local Authorities (if imminent)
- **Action**: Immediate intervention

---

### 6. IMMINENT_DANGER
**Active emergency or immediate physical danger**

**Examples**:
- "Active shooter in the store"
- "Fire in the building"
- "Someone having a medical emergency"

**Response**:
- **911 immediately**
- **Emergency procedures**
- **Store security alert**
- **Evacuation if needed**

**Example**:
```
User: "There's an active shooter in the store"

Response: "**IMMEDIATE DANGER - TAKE ACTION NOW**

**If you or someone else is in immediate danger:**
• Call 911 immediately
• Contact Store Security: Ext. 999
• Go to a safe location
• Follow emergency evacuation procedures

**Your Safety is Priority:**
Please reach out to emergency services right now. Help is available immediately.

This conversation has been flagged for immediate follow-up by our safety team.

*Reference: SAFE-C9A12D4F6E8B*"
```

**Escalation**:
- **Priority**: CRITICAL_IMMEDIATE
- **Recipients**: Security, Local Authorities, Crisis Response Team
- **Action**: Immediate emergency response

---

## Components

### 1. SafetyClassifier

**Location**: `backend/safety/classifier.py`

**Purpose**: Detect and classify safety concerns in user messages

**Classification Layers**:

1. **Imminent Danger Check** (Highest Priority)
   - Active shooter, fire, medical emergency
   - Immediate routing to emergency response

2. **Harm to Others Check**
   - Threats, violence, weapons
   - Pattern matching + semantic analysis

3. **Self-Harm Check**
   - Suicidal ideation, self-harm intent
   - Conservative detection (false positive > false negative)

4. **Emotional Distress Check**
   - Panic, severe stress, crisis
   - Multiple severity levels

5. **Profanity Check**
   - Offensive language detection
   - Context-aware severity

6. **LLM Semantic Analysis** (Optional)
   - Vertex AI Gemini for nuanced understanding
   - Catches cases patterns might miss
   - Can be disabled for cost control

**Usage**:
```python
from backend.safety import SafetyClassifier

classifier = SafetyClassifier(
    project_id="your-project",
    use_llm_classification=True
)

classification = classifier.classify(
    message="User message here",
    context={
        'store_id': 'NY_001',
        'device_id': 'CT40_123',
        'user_id': 'user_456'
    }
)

print(f"Category: {classification.category}")
print(f"Severity: {classification.severity}")
print(f"Confidence: {classification.confidence}")
print(f"Patterns: {classification.detected_patterns}")
```

**Configuration**:
```python
# Enable/disable LLM classification
use_llm_classification=True  # Default: True

# LLM is used when:
# - Pattern-based classification is uncertain
# - Confidence < 0.7
# - Category is SAFE_OPERATIONAL but message seems concerning
```

---

### 2. SafetyPolicyEngine

**Location**: `backend/safety/policy_engine.py`

**Purpose**: Generate appropriate responses based on classification

**Response Components**:
- **Message**: Supportive text with resources
- **Support Resources**: Phone numbers, services
- **Recipients**: Who should be notified
- **Escalation Priority**: NONE, MEDIUM, HIGH, CRITICAL, CRITICAL_IMMEDIATE
- **Allow Continuation**: Whether chatbot can continue conversation

**Usage**:
```python
from backend.safety import SafetyPolicyEngine

policy_engine = SafetyPolicyEngine()

response = policy_engine.generate_response(classification)

print(response.message)  # Display to user
print(response.support_resources)  # Show resources
print(response.requires_escalation)  # True/False
print(response.escalation_priority)  # Priority level
```

**Support Resources**:
```python
{
    'name': '988 Suicide & Crisis Lifeline',
    'phone': '988',
    'description': '24/7 free and confidential support',
    'available': '24/7'
}
```

**Configurable Resources**: Edit `backend/safety/policy_engine.py`:
```python
self.support_resources = {
    'mental_health': {
        'name': 'Employee Assistance Program (EAP)',
        'phone': '1-800-YOUR-EAP',  # <-- Update this
        'available': '24/7'
    },
    'crisis': {
        'name': '988 Suicide & Crisis Lifeline',
        'phone': '988'
    },
    # ... more resources
}
```

---

### 3. ConfidentialReportingService

**Location**: `backend/safety/reporting_service.py`

**Purpose**: Securely escalate safety incidents to appropriate teams

**Security Features**:
- **User ID Anonymization**: SHA-256 one-way hash
- **Message Encryption**: Fernet symmetric encryption
- **Access Controls**: Firestore security rules
- **Audit Logging**: All access logged
- **Auto-Deletion**: Retention policies (30-365 days)

**Storage**:
- **Firestore Collection**: `safety_incidents_confidential`
- **Encryption Keys**: Google Secret Manager
- **Routing**: Pub/Sub topics by priority

**Report Structure**:
```python
{
    'report_id': 'SAFE-A3F92E1BC45D',
    'timestamp': '2026-01-09T14:30:00Z',
    'classification_category': 'self_harm_risk',
    'severity_level': 'CRITICAL',
    'escalation_priority': 'CRITICAL_IMMEDIATE',

    'anonymized_user_id': '7f3a9b2c4e8d1f6a',  # One-way hash
    'device_id': 'CT40_123',
    'store_id': 'NY_001',
    'session_id': 'sess_abc123',

    'encrypted_message': 'gAAAAA...',  # Fernet encrypted
    'encryption_key_version': 'v1',

    'detected_patterns': ['kill myself'],
    'confidence_score': 0.95,
    'classification_reasoning': 'Explicit self-harm ideation',

    'recipients': ['hr', 'mental_health', 'store_manager'],
    'requires_followup': True,

    'retention_days': 365,
    'access_log': []
}
```

**Usage**:
```python
from backend.safety import ConfidentialReportingService

reporting = ConfidentialReportingService(project_id="your-project")

report_id = reporting.submit_report(
    user_id="user_123",
    message="Original user message",
    classification={...},
    policy_response={...},
    context={'store_id': 'NY_001'}
)

print(f"Report ID: {report_id}")
```

**Retrieval** (Authorized Only):
```python
report = reporting.get_report(
    report_id="SAFE-A3F92E1BC45D",
    accessor_id="hr_manager_456",
    purpose="Follow-up on safety incident"
)

# Automatically decrypts message
print(report['decrypted_message'])

# Access is logged in access_log
print(report['access_log'])
```

**Pub/Sub Topics**:
- `safety-medium`: Medium priority (90 day retention)
- `safety-high`: High priority (180 day retention)
- `safety-critical`: Critical priority (365 day retention)
- `safety-emergency`: Immediate action required

---

## Integration Flow

### API Endpoint Integration

**Location**: `backend/api/main.py`

**Flow**:
```python
@app.post("/ask")
def ask_question(query: Query):
    # STEP 1: Safety Classification
    classification = safety_classifier.classify(query.question, context={...})

    # STEP 2: Check if safety concern
    if classification.category != SafetyCategory.SAFE_OPERATIONAL:
        # Generate safety response
        safety_response = safety_policy.generate_response(classification)

        # STEP 3: Escalate if needed
        if safety_response.requires_escalation:
            report_id = safety_reporting.submit_report(...)
            response_message = safety_response.message + f"\n\n*Reference: {report_id}*"

        # Return safety response (skip RAG)
        return {
            "answer": response_message,
            "safety_classification": classification.category.value,
            "support_resources": safety_response.support_resources,
            "is_safety_response": True
        }

    # STEP 4: If safe, proceed to RAG
    rag_response = rag.ask(query.question)
    return rag_response
```

### Request/Response Format

**Request**:
```json
{
  "question": "What is the return policy?",
  "store_id": "NY_001",
  "user_id": "user_123",
  "device_id": "CT40_456",
  "session_id": "sess_abc123"
}
```

**Response (Safe)**:
```json
{
  "answer": "The return policy allows...",
  "sources": [...],
  "safety_classification": "safe_operational",
  "is_safety_response": false
}
```

**Response (Safety Concern)**:
```json
{
  "answer": "Your safety is the most important thing...\n\n*Reference: SAFE-A3F92E1BC45D*",
  "safety_classification": "self_harm_risk",
  "severity": "CRITICAL",
  "support_resources": [
    {
      "name": "988 Suicide & Crisis Lifeline",
      "phone": "988",
      "description": "24/7 free and confidential support"
    }
  ],
  "allow_continuation": false,
  "is_safety_response": true
}
```

---

## Response Examples

### Example 1: Safe Operational Question

**Input**: "What is the return policy for electronics?"

**Classification**:
- Category: SAFE_OPERATIONAL
- Severity: NONE
- Confidence: 0.98

**Response**: Standard RAG answer about return policies

---

### Example 2: Profanity (Low Severity)

**Input**: "This damn scanner won't work"

**Classification**:
- Category: PROFANITY_ONLY
- Severity: LOW
- Confidence: 0.85

**Response**:
```
I'm here to help with your work-related questions.

Please keep the conversation professional so I can assist you better.

What issue are you experiencing with the scanner?
```

---

### Example 3: Emotional Distress (Medium)

**Input**: "I'm so overwhelmed, everything is too much"

**Classification**:
- Category: EMOTIONAL_DISTRESS
- Severity: MEDIUM
- Confidence: 0.82

**Response**:
```
I hear that things might be challenging right now. Resources are available if you need them.

**Support Available:**
• Employee Assistance Program: 1-800-XXX-XXXX (confidential counseling)
• Speak with your Store Manager
• HR Support: 1-800-XXX-XXXX

**Taking Care of Yourself:**
It's okay to reach out when you need support. These resources are here to help.

How else can I assist you today?
```

**Escalation**: Report sent to HR (MEDIUM priority)

---

### Example 4: Self-Harm Risk (Critical)

**Input**: "I can't take this anymore, going to end it tonight"

**Classification**:
- Category: SELF_HARM_RISK
- Severity: CRITICAL
- Confidence: 0.96
- Patterns: ["end it", "tonight"]

**Response**:
```
Your safety is the most important thing right now.

**Immediate Support Available:**
• 988 Suicide & Crisis Lifeline: Call or text 988 (24/7)
• Employee Assistance Program: 1-800-XXX-XXXX (24/7, confidential)
• If this is a medical emergency, call 911

**You Are Not Alone:**
These feelings are temporary, and support is available. Speaking with a trained
professional can help.

**Confidential & Private:**
Your privacy is protected. These resources are confidential and separate from
your employment record.

I care about your wellbeing and want to ensure you get the support you deserve.

*Reference: SAFE-A3F92E1BC45D*
```

**Escalation**:
- Priority: CRITICAL_IMMEDIATE
- Recipients: HR, Mental Health Team, Store Manager
- Allow Continuation: False
- Report: Encrypted, audit-logged

---

### Example 5: Harm to Others (High)

**Input**: "I'm going to hurt my supervisor tomorrow"

**Classification**:
- Category: HARM_TO_OTHERS_RISK
- Severity: HIGH
- Confidence: 0.91
- Patterns: ["hurt", "supervisor"]

**Response**:
```
I'm concerned about what you've mentioned. Everyone's safety is important.

**Please Contact:**
• Store Security: Ext. 999
• Your Store Manager
• Employee Assistance Program: 1-800-XXX-XXXX (confidential support)

**Workplace Safety:**
We're committed to maintaining a safe environment for everyone. Speaking with
management helps address concerns appropriately.

**Confidential Resources:**
If you're experiencing stress or frustration, EAP provides confidential
counseling and support.

*Reference: SAFE-B7E84F2AD91C*
```

**Escalation**:
- Priority: CRITICAL_IMMEDIATE
- Recipients: Security, Store Manager, HR
- Allow Continuation: False
- Immediate intervention triggered

---

### Example 6: Imminent Danger

**Input**: "Active shooter in the store right now"

**Classification**:
- Category: IMMINENT_DANGER
- Severity: CRITICAL
- Confidence: 0.99
- Patterns: ["active shooter", "right now"]

**Response**:
```
**IMMEDIATE DANGER - TAKE ACTION NOW**

**If you or someone else is in immediate danger:**
• Call 911 immediately
• Contact Store Security: Ext. 999
• Go to a safe location
• Follow emergency evacuation procedures

**Your Safety is Priority:**
Please reach out to emergency services right now. Help is available immediately.

This conversation has been flagged for immediate follow-up by our safety team.

*Reference: SAFE-C9A12D4F6E8B*
```

**Escalation**:
- Priority: CRITICAL_IMMEDIATE
- Recipients: Security, Local Authorities, Crisis Response
- Allow Continuation: False
- Emergency response activated

---

## Privacy & Compliance

### Data Protection

**User ID Anonymization**:
```python
# One-way SHA-256 hash with salt
anonymized_id = hashlib.sha256(f"{user_id}{salt}".encode()).hexdigest()[:16]

# Cannot be reversed to original user_id
# Allows correlation of multiple reports from same user
# Does not expose user identity
```

**Message Encryption**:
```python
# Fernet symmetric encryption
from cryptography.fernet import Fernet

# Key stored in Google Secret Manager
key = secret_manager.access_secret_version("safety-encryption-key")
fernet = Fernet(key)

# Encrypt message
encrypted = fernet.encrypt(message.encode()).decode()

# Only authorized personnel can decrypt
decrypted = fernet.decrypt(encrypted.encode()).decode()
```

### Access Controls

**Firestore Security Rules** (Example):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Safety reports collection
    match /safety_incidents_confidential/{reportId} {
      // Only service accounts can write
      allow create: if request.auth.token.email.matches('.*@your-project.iam.gserviceaccount.com');

      // Only authorized roles can read
      allow read: if request.auth.token.email in [
        'hr-team@your-company.com',
        'security@your-company.com',
        'mental-health@your-company.com'
      ];

      // No public access
      allow list, delete: if false;
    }

    // Audit log (append-only)
    match /safety_audit_log/{logId} {
      allow create: if request.auth != null;
      allow read, update, delete: if false;  // Append-only
    }
  }
}
```

### Audit Logging

**Every access is logged**:
```python
{
    'timestamp': '2026-01-09T14:35:22Z',
    'action': 'ACCESS_GRANTED: Follow-up investigation',
    'report_id': 'SAFE-A3F92E1BC45D',
    'accessor_id': 'hr_manager_456',
    'service': 'confidential_reporting'
}
```

**Audit log is**:
- **Append-only** (cannot be deleted or modified)
- **Stored separately** from reports
- **Reviewed regularly** for compliance
- **Retained indefinitely** for legal compliance

### Data Retention

**Automatic Deletion**:
```python
retention_map = {
    'LOW': 30,      # 30 days
    'MEDIUM': 90,   # 90 days
    'HIGH': 180,    # 6 months
    'CRITICAL': 365  # 1 year
}
```

**Cleanup Job** (Cloud Scheduler):
```bash
# Run daily via Cloud Scheduler
0 2 * * * /cleanup_expired_reports.py
```

### GDPR/CCPA Compliance

✅ **Right to Access**: Users can request their reports via HR
✅ **Right to Deletion**: Automated retention + manual deletion available
✅ **Data Minimization**: Only necessary data collected
✅ **Purpose Limitation**: Data only used for safety purposes
✅ **Encryption**: At rest and in transit
✅ **Access Controls**: Role-based access
✅ **Audit Logging**: Full access trail
✅ **Anonymization**: User IDs hashed

---

## Configuration

### Environment Variables

**Required**:
```bash
# Google Cloud Project ID
PROJECT_ID=your-gcp-project-id

# User ID salt for anonymization (change in production!)
USER_ID_SALT=your-random-salt-string-here
```

**Optional**:
```bash
# Disable LLM classification to save costs
SAFETY_LLM_ENABLED=false

# Custom retention periods (days)
SAFETY_RETENTION_LOW=30
SAFETY_RETENTION_MEDIUM=90
SAFETY_RETENTION_HIGH=180
SAFETY_RETENTION_CRITICAL=365
```

### Support Resources Configuration

**Edit**: `backend/safety/policy_engine.py`

```python
self.support_resources = {
    'mental_health': {
        'name': 'Employee Assistance Program (EAP)',
        'phone': '1-800-YOUR-EAP-NUMBER',  # <-- UPDATE
        'available': '24/7',
        'description': 'Confidential counseling and support'
    },
    'crisis': {
        'name': '988 Suicide & Crisis Lifeline',
        'phone': '988'  # Standard US crisis line
    },
    'hr': {
        'name': 'HR Support',
        'phone': '1-800-YOUR-HR-NUMBER',  # <-- UPDATE
        'available': 'Business hours'
    },
    'security': {
        'name': 'Store Security',
        'extension': 'Ext. YOUR-SECURITY-EXT',  # <-- UPDATE
        'description': 'Immediate store security assistance'
    }
}
```

### Pub/Sub Topics Setup

**Create topics**:
```bash
gcloud pubsub topics create safety-medium --project=your-project
gcloud pubsub topics create safety-high --project=your-project
gcloud pubsub topics create safety-critical --project=your-project
gcloud pubsub topics create safety-emergency --project=your-project
```

**Create subscriptions**:
```bash
# HR team subscription (all priorities)
gcloud pubsub subscriptions create hr-safety-alerts \
  --topic=safety-high \
  --project=your-project

# Security team (critical only)
gcloud pubsub subscriptions create security-alerts \
  --topic=safety-emergency \
  --project=your-project

# Mental health team (self-harm cases)
gcloud pubsub subscriptions create mental-health-alerts \
  --topic=safety-critical \
  --project=your-project
```

### Secret Manager Setup

**Create encryption key secret**:
```bash
# Generate a Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Store in Secret Manager
echo "YOUR_GENERATED_KEY" | gcloud secrets create safety-encryption-key \
  --data-file=- \
  --project=your-project

# Grant access to App Engine service account
gcloud secrets add-iam-policy-binding safety-encryption-key \
  --member="serviceAccount:your-project@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=your-project
```

---

## Testing

### Run Unit Tests

```bash
# Install pytest
pip install pytest pytest-cov

# Run all safety tests
pytest tests/test_safety.py -v

# Run with coverage
pytest tests/test_safety.py --cov=backend/safety --cov-report=html

# Run specific test class
pytest tests/test_safety.py::TestSafetyClassifier -v

# Run specific test
pytest tests/test_safety.py::TestSafetyClassifier::test_self_harm_detection_critical -v
```

### Test Coverage

The test suite covers:
- ✅ Safe operational messages
- ✅ Self-harm detection (all severity levels)
- ✅ Harm to others detection
- ✅ Emotional distress detection
- ✅ Profanity detection
- ✅ Imminent danger detection
- ✅ Policy response generation
- ✅ Escalation priority assignment
- ✅ Resource formatting
- ✅ End-to-end integration

### Manual Testing

**Test Cases**:

```python
# Test 1: Safe message
test_messages = [
    "What is the return policy?",
    "How do I process an exchange?",
]

# Test 2: Profanity
test_messages = [
    "This damn scanner won't work",
    "What the hell is wrong with this system",
]

# Test 3: Emotional distress
test_messages = [
    "I'm feeling really stressed today",
    "I'm so overwhelmed I can't think straight",
    "Having a panic attack right now",
]

# Test 4: Self-harm (use with caution)
test_messages = [
    "I wish I wasn't here",
    "I want to disappear",
    "I can't take this anymore",
]

# Test 5: Harm to others
test_messages = [
    "I'm so angry at my coworker",
    "I want to hurt my manager",
]

# Test 6: Imminent danger
test_messages = [
    "There's a fire in the building",
    "Someone collapsed, need help",
]
```

**Testing Script**:
```python
from backend.safety import SafetyClassifier, SafetyPolicyEngine

classifier = SafetyClassifier(project_id="your-project", use_llm_classification=False)
policy_engine = SafetyPolicyEngine()

for message in test_messages:
    classification = classifier.classify(message)
    response = policy_engine.generate_response(classification)

    print(f"\n{'='*60}")
    print(f"Message: {message}")
    print(f"Category: {classification.category.value}")
    print(f"Severity: {classification.severity.value}")
    print(f"Confidence: {classification.confidence}")
    print(f"\nResponse:\n{response.message}")
    print(f"Escalation: {response.requires_escalation}")
```

---

## Monitoring & Reporting

### Metrics to Track

**Classification Metrics**:
- Total messages classified
- Distribution by category
- Distribution by severity
- Average confidence scores
- LLM usage rate

**Escalation Metrics**:
- Total escalations
- Escalations by priority
- Response time (first contact)
- Resolution time

**System Metrics**:
- Classification latency
- LLM latency (when enabled)
- False positive rate (requires human review)
- False negative rate (requires human review)

### Dashboard Queries

**Firestore Query Examples**:

```python
# Count reports by category (last 7 days)
from datetime import datetime, timedelta
from google.cloud import firestore

db = firestore.Client()
seven_days_ago = datetime.utcnow() - timedelta(days=7)

reports = db.collection('safety_incidents_confidential')\
    .where('timestamp', '>=', seven_days_ago.isoformat())\
    .stream()

category_counts = {}
for report in reports:
    data = report.to_dict()
    category = data['classification_category']
    category_counts[category] = category_counts.get(category, 0) + 1

print(category_counts)
```

**Cloud Logging Queries**:

```
# All safety classifications
resource.type="gae_app"
jsonPayload.safety_classification!="safe_operational"

# Critical escalations
resource.type="gae_app"
jsonPayload.escalation_priority="CRITICAL_IMMEDIATE"

# LLM classification requests
resource.type="gae_app"
textPayload=~"LLM semantic analysis"
```

### Alerting

**Setup Alerts for**:

1. **Critical Escalations**: Alert security team immediately
2. **High Volume**: Unusual number of safety incidents
3. **System Errors**: Classification failures
4. **Encryption Key Access**: Unauthorized access attempts

**Example Alert Policy** (Cloud Monitoring):
```yaml
displayName: "Critical Safety Escalation Alert"
conditions:
  - displayName: "Critical escalation detected"
    conditionThreshold:
      filter: |
        resource.type="gae_app"
        jsonPayload.escalation_priority="CRITICAL_IMMEDIATE"
      comparison: COMPARISON_GT
      thresholdValue: 0
      duration: 0s
notificationChannels:
  - "projects/YOUR_PROJECT/notificationChannels/SECURITY_TEAM"
  - "projects/YOUR_PROJECT/notificationChannels/HR_TEAM"
alertStrategy:
  autoClose: 3600s  # 1 hour
```

### Regular Reviews

**Weekly**:
- Review all CRITICAL escalations
- Check false positive rate
- Update patterns based on new cases

**Monthly**:
- Analyze trends by category
- Review support resource effectiveness
- Update response templates if needed
- Audit access logs

**Quarterly**:
- Review retention policies
- Update security rules
- Compliance audit
- Staff training updates

---

## Best Practices

### For Administrators

1. **Keep Support Resources Updated**: Ensure phone numbers and contacts are current
2. **Review Patterns Regularly**: Add new detection patterns as needed
3. **Monitor False Positives**: Adjust confidence thresholds if too many false alarms
4. **Train Staff**: Ensure HR/Security know how to access and respond to reports
5. **Test Regularly**: Run test cases monthly to ensure system works correctly
6. **Rotate Encryption Keys**: Annually rotate Secret Manager keys
7. **Audit Access**: Monthly review of who accessed what reports
8. **Update Templates**: Refine response templates based on feedback

### For Developers

1. **Never Log Sensitive Data**: Don't log user messages or decrypted content
2. **Use Environment Variables**: Don't hardcode secrets or phone numbers
3. **Test Before Deploy**: Run full test suite before deploying changes
4. **Monitor Latency**: Keep classification under 500ms
5. **Handle Errors Gracefully**: If classification fails, err on side of safety
6. **Document Changes**: Update this doc when adding features
7. **Review Security**: Regular security audits of access controls

### For HR/Security Teams

1. **Respond Promptly**: CRITICAL_IMMEDIATE cases require immediate action
2. **Maintain Confidentiality**: Never discuss cases outside authorized channels
3. **Document Follow-ups**: Update access logs when accessing reports
4. **Provide Resources**: Ensure users get promised support
5. **Report Issues**: If system misclassifies, notify development team
6. **Training**: Stay current on mental health first aid and de-escalation

---

## Support & Questions

For questions about the Safety Framework:

- **Technical Issues**: Contact development team
- **Safety Concerns**: Contact HR or Security immediately
- **Feature Requests**: Submit via your standard process
- **Compliance Questions**: Contact legal/compliance team

---

**Version**: 1.0.0
**Last Updated**: 2026-01-09
**Maintained By**: AI Platform Engineering Team
**Classification**: INTERNAL USE ONLY

