# Safety Framework Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Support Resources

Edit `backend/safety/config.py`:

```python
SUPPORT_RESOURCES = {
    'mental_health': {
        'name': 'Employee Assistance Program (EAP)',
        'phone': '1-800-YOUR-EAP',  # ⬅️ UPDATE THIS
        'available': '24/7'
    },
    'hr': {
        'name': 'HR Support Line',
        'phone': '1-800-YOUR-HR',  # ⬅️ UPDATE THIS
        'available': 'Business hours'
    },
    'security': {
        'name': 'Store Security',
        'extension': 'Ext. YOUR-EXT',  # ⬅️ UPDATE THIS
    }
}
```

### Step 3: Set Environment Variables

```bash
# Required for production
export USER_ID_SALT="your-unique-random-salt-here"

# Optional
export SAFETY_LLM_ENABLED="true"  # Enable LLM semantic analysis
export EAP_PHONE="1-800-XXX-XXXX"
export HR_PHONE="1-800-XXX-XXXX"
export SECURITY_EXTENSION="Ext. 999"
```

### Step 4: Verify Configuration

```bash
python backend/safety/config.py
```

Expected output:
```
SAFETY FRAMEWORK CONFIGURATION SUMMARY
======================================================================
📊 LLM Classification:
   Enabled: True
   Model: gemini-2.0-flash-exp

📞 Support Resources:
   Crisis Line: 988
   EAP: 1-800-YOUR-EAP
   HR: 1-800-YOUR-HR
   Security: Ext. YOUR-EXT
```

### Step 5: Run Tests

```bash
pytest tests/test_safety.py -v
```

Expected: All tests pass ✅

---

## 📋 How It Works

### User Flow

```
User asks question
       ↓
Safety Classifier analyzes message
       ↓
┌──────────┬──────────────────┐
│   SAFE   │   SAFETY ISSUE   │
└──────────┴──────────────────┘
     ↓              ↓
RAG Answer    Safety Response
              + Resources
              + Escalation (if needed)
```

### Safety Categories

| Category | Example | Response |
|----------|---------|----------|
| **SAFE_OPERATIONAL** | "What is the return policy?" | Standard RAG answer |
| **PROFANITY_ONLY** | "This damn scanner won't work" | Professional reminder + Continue |
| **EMOTIONAL_DISTRESS** | "I'm so stressed out" | Support resources + EAP |
| **SELF_HARM_RISK** | "I want to end it all" | **988 Crisis Line** + Escalation |
| **HARM_TO_OTHERS_RISK** | "I want to hurt my manager" | **Security alert** + Escalation |
| **IMMINENT_DANGER** | "Active shooter" | **911** + Emergency response |

---

## 🔧 Testing

### Test Safe Message

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the return policy?",
    "store_id": "NY_001"
  }'
```

**Expected**: Normal RAG response with `"is_safety_response": false`

### Test Safety Concern

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I am feeling very stressed and overwhelmed",
    "store_id": "NY_001",
    "user_id": "test_user_123"
  }'
```

**Expected**: Safety response with EAP resources and `"is_safety_response": true`

### Run Full Test Suite

```bash
# Quick test
pytest tests/test_safety.py

# With coverage report
pytest tests/test_safety.py --cov=backend/safety --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## 🔒 GCP Setup (For Escalation & Reporting)

### 1. Create Pub/Sub Topics

```bash
PROJECT_ID="your-project-id"

gcloud pubsub topics create safety-medium --project=$PROJECT_ID
gcloud pubsub topics create safety-high --project=$PROJECT_ID
gcloud pubsub topics create safety-critical --project=$PROJECT_ID
gcloud pubsub topics create safety-emergency --project=$PROJECT_ID
```

### 2. Create Subscriptions

```bash
# HR team receives all escalations
gcloud pubsub subscriptions create hr-safety-alerts \
  --topic=safety-high \
  --project=$PROJECT_ID

# Security team receives critical/emergency only
gcloud pubsub subscriptions create security-alerts \
  --topic=safety-emergency \
  --project=$PROJECT_ID
```

### 3. Create Encryption Key

```bash
# Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Output: gAAAAABh... (copy this)

# Store in Secret Manager
echo "YOUR_GENERATED_KEY" | gcloud secrets create safety-encryption-key \
  --data-file=- \
  --project=$PROJECT_ID

# Grant access to service account
gcloud secrets add-iam-policy-binding safety-encryption-key \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID
```

### 4. Create Firestore Collection

Firestore will auto-create collections, but set security rules:

```javascript
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /safety_incidents_confidential/{reportId} {
      allow create: if request.auth != null;
      allow read: if request.auth.token.email in [
        'hr@your-company.com',
        'security@your-company.com'
      ];
      allow list, update, delete: if false;
    }
  }
}
```

Deploy rules:
```bash
gcloud firestore rules deploy firestore.rules --project=$PROJECT_ID
```

---

## 📊 Monitoring

### View Recent Safety Classifications

```bash
# Cloud Logging query
gcloud logging read '
  resource.type="gae_app"
  jsonPayload.safety_classification!="safe_operational"
' --limit 10 --format json
```

### View Critical Escalations

```bash
gcloud logging read '
  resource.type="gae_app"
  jsonPayload.escalation_priority="CRITICAL_IMMEDIATE"
' --limit 5 --format json
```

### Pull Pub/Sub Messages

```bash
# Check HR alerts
gcloud pubsub subscriptions pull hr-safety-alerts \
  --limit=5 \
  --project=$PROJECT_ID
```

---

## 🎯 Common Use Cases

### Use Case 1: Store Associate Having Bad Day

**Input**: "Having a really rough day today"

**Classification**: EMOTIONAL_DISTRESS (LOW-MEDIUM)

**Response**:
- Supportive message
- EAP resources
- Option to continue with work questions
- No escalation (unless HIGH severity)

### Use Case 2: Frustrated with Technology

**Input**: "This f***ing scanner never works!"

**Classification**: PROFANITY_ONLY (LOW)

**Response**:
- Gentle reminder to keep conversation professional
- Offer to help with the actual issue
- Continue conversation normally

### Use Case 3: Serious Mental Health Concern

**Input**: "I don't want to be here anymore"

**Classification**: SELF_HARM_RISK (HIGH)

**Response**:
- **Immediate**: 988 Crisis Line
- **Support**: EAP resources
- **Escalation**: Report to HR + Mental Health Team
- **Block**: Cannot continue regular conversation

### Use Case 4: Workplace Threat

**Input**: "I'm bringing a weapon tomorrow"

**Classification**: HARM_TO_OTHERS_RISK (CRITICAL)

**Response**:
- **Immediate**: Contact Security + Store Manager
- **Escalation**: CRITICAL_IMMEDIATE to Security team
- **Action**: Immediate intervention protocol
- **Block**: Cannot continue conversation

### Use Case 5: Emergency Situation

**Input**: "Fire in the stockroom!"

**Classification**: IMMINENT_DANGER (CRITICAL)

**Response**:
- **Immediate**: Call 911
- **Alert**: Store Security
- **Evacuate**: Follow emergency procedures
- **Escalation**: Emergency response team notified

---

## ⚙️ Configuration Options

### Disable LLM Classification (Cost Savings)

```bash
export SAFETY_LLM_ENABLED="false"
```

Pattern-based detection only. Faster, cheaper, but less accurate for nuanced cases.

### Adjust Retention Periods

```bash
export SAFETY_RETENTION_LOW="30"      # 30 days
export SAFETY_RETENTION_MEDIUM="90"   # 90 days
export SAFETY_RETENTION_HIGH="180"    # 6 months
export SAFETY_RETENTION_CRITICAL="365" # 1 year
```

### Customize Response Templates

Edit `backend/safety/response_templates.py`:

```python
RESPONSE_TEMPLATES = {
    'self_harm_risk': {
        'high': """Your safety is important..."""  # Customize message
    }
}
```

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
tail -50 backend.log

# Common issues:
# 1. Missing dependencies
pip install -r requirements.txt

# 2. Firestore/PubSub credentials
gcloud auth application-default login
```

### Classification not working

```python
# Test classifier directly
from backend.safety import SafetyClassifier

classifier = SafetyClassifier(
    project_id="zensai-poc",
    use_llm_classification=False  # Disable LLM for testing
)

result = classifier.classify("test message")
print(result.category)
print(result.severity)
```

### Can't submit reports

```bash
# Check Firestore permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  | grep firestore

# Grant if needed
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Pub/Sub not working

```bash
# Check topics exist
gcloud pubsub topics list --project=YOUR_PROJECT_ID

# Check subscriptions
gcloud pubsub subscriptions list --project=YOUR_PROJECT_ID

# Test manually
gcloud pubsub topics publish safety-high \
  --message='{"test": "message"}' \
  --project=YOUR_PROJECT_ID
```

---

## 📚 Next Steps

1. **Read Full Documentation**: [SAFETY_FRAMEWORK.md](SAFETY_FRAMEWORK.md)
2. **Customize Resources**: Update phone numbers in `config.py`
3. **Set Up GCP**: Create Pub/Sub topics, Firestore, Secret Manager
4. **Deploy**: Follow [DEPLOYMENT.md](DEPLOYMENT.md) for App Engine
5. **Monitor**: Set up Cloud Logging alerts for critical incidents
6. **Train Staff**: Ensure HR/Security know how to access reports

---

## 🆘 Support

- **Technical Issues**: Development team
- **Safety Concerns**: HR or Security (immediate)
- **Configuration Help**: See [SAFETY_FRAMEWORK.md](SAFETY_FRAMEWORK.md)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-09
**Status**: ✅ Production Ready
