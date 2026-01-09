# Safety Framework - Deployment Addendum

## Additional Deployment Steps for Safety Framework

This document extends the main [DEPLOYMENT.md](DEPLOYMENT.md) with specific steps required for the Safety & Escalation Framework.

---

## Prerequisites

Before deploying the safety framework to App Engine, ensure you have completed the main deployment prerequisites from [DEPLOYMENT.md](DEPLOYMENT.md), plus the following:

### Required GCP APIs

Enable these additional APIs:

```bash
gcloud services enable firestore.googleapis.com --project=$PROJECT_ID
gcloud services enable pubsub.googleapis.com --project=$PROJECT_ID
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID
```

---

## Step-by-Step Safety Framework Setup

### 1. Create Pub/Sub Topics for Escalation

```bash
# Set your project ID
PROJECT_ID="zensai-poc"  # Change to your project

# Create topics for different priority levels
gcloud pubsub topics create safety-medium --project=$PROJECT_ID
gcloud pubsub topics create safety-high --project=$PROJECT_ID
gcloud pubsub topics create safety-critical --project=$PROJECT_ID
gcloud pubsub topics create safety-emergency --project=$PROJECT_ID

# Verify topics created
gcloud pubsub topics list --project=$PROJECT_ID | grep safety
```

### 2. Create Pub/Sub Subscriptions

```bash
# HR team receives high-priority alerts
gcloud pubsub subscriptions create hr-safety-alerts \
  --topic=safety-high \
  --project=$PROJECT_ID

# HR also receives critical alerts
gcloud pubsub subscriptions create hr-critical-alerts \
  --topic=safety-critical \
  --project=$PROJECT_ID

# Security team receives emergency alerts
gcloud pubsub subscriptions create security-emergency-alerts \
  --topic=safety-emergency \
  --project=$PROJECT_ID

# Mental health team receives critical mental health cases
gcloud pubsub subscriptions create mental-health-alerts \
  --topic=safety-critical \
  --project=$PROJECT_ID

# Verify subscriptions
gcloud pubsub subscriptions list --project=$PROJECT_ID | grep safety
```

### 3. Generate and Store Encryption Key

```bash
# Generate a Fernet encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Output will look like: gAAAAABhxyz123...
# COPY THIS KEY - you'll need it in the next step

# Store the key in Secret Manager
# Replace YOUR_GENERATED_KEY with the key from previous command
echo "YOUR_GENERATED_KEY" | gcloud secrets create safety-encryption-key \
  --data-file=- \
  --replication-policy="automatic" \
  --project=$PROJECT_ID

# Verify secret created
gcloud secrets describe safety-encryption-key --project=$PROJECT_ID
```

### 4. Grant Service Account Access to Secret

```bash
# Grant App Engine service account access to the encryption key
gcloud secrets add-iam-policy-binding safety-encryption-key \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID

# Verify permissions
gcloud secrets get-iam-policy safety-encryption-key --project=$PROJECT_ID
```

### 5. Configure Firestore

```bash
# Create Firestore database (if not already created)
# Choose Native mode
gcloud firestore databases create --location=us-central --project=$PROJECT_ID

# Note: Collections will be auto-created when first report is submitted
# Collections: safety_incidents_confidential, safety_audit_log
```

### 6. Deploy Firestore Security Rules

Create `firestore.rules`:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Safety incident reports - highly restricted
    match /safety_incidents_confidential/{reportId} {
      // Service accounts can create reports
      allow create: if request.auth != null
        && request.auth.token.email.matches('.*@' + request.project + '.iam.gserviceaccount.com');

      // Only authorized personnel can read
      // TODO: Replace with your actual HR/Security email addresses
      allow read: if request.auth.token.email in [
        'hr@your-company.com',
        'security@your-company.com',
        'mental-health@your-company.com'
      ];

      // No public list, update, or delete
      allow list, update, delete: if false;
    }

    // Audit log - append-only
    match /safety_audit_log/{logId} {
      allow create: if request.auth != null;
      allow read, update, delete: if false;  // Append-only
    }

    // All other collections - default deny
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

Deploy rules:

```bash
gcloud firestore rules deploy firestore.rules --project=$PROJECT_ID
```

### 7. Set Environment Variables

Update your `app.yaml` to include safety-specific environment variables:

```yaml
env_variables:
  PROJECT_ID: "zensai-poc"  # Your project ID
  PYTHONUNBUFFERED: "1"

  # Safety Framework Configuration
  USER_ID_SALT: "YOUR_UNIQUE_RANDOM_SALT_HERE"  # CHANGE THIS!
  SAFETY_LLM_ENABLED: "true"  # Set to "false" to disable LLM classification

  # Support Resources (optional - can also edit config.py)
  EAP_PHONE: "1-800-XXX-XXXX"  # Your EAP number
  HR_PHONE: "1-800-XXX-XXXX"   # Your HR number
  SECURITY_EXTENSION: "Ext. 999"  # Your security extension
```

**Important**: Generate a unique, random `USER_ID_SALT`:

```bash
# Generate a random salt
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output and use it as USER_ID_SALT in app.yaml
```

### 8. Update Support Resources

Edit `backend/safety/config.py` and update these values:

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
        'extension': 'Ext. YOUR-SECURITY',  # ⬅️ UPDATE THIS
    }
}
```

### 9. Grant Additional IAM Permissions

```bash
# Grant Firestore access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/datastore.user"

# Grant Pub/Sub publisher access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

# Verify permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$PROJECT_ID@appspot.gserviceaccount.com"
```

### 10. Test Locally Before Deploying

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_safety.py -v

# Expected: All tests pass ✅

# Test configuration
python backend/safety/config.py

# Expected: No warnings about missing configuration
```

### 11. Deploy to App Engine

```bash
# Deploy backend with safety framework
gcloud app deploy app.yaml --project=$PROJECT_ID

# Wait for deployment to complete...
# Test the deployment
curl https://$PROJECT_ID.uc.r.appspot.com/health

# Expected: {"status": "healthy", "project_id": "zensai-poc"}
```

### 12. Verify Safety Framework in Production

```bash
# Test safe question
curl -X POST https://$PROJECT_ID.uc.r.appspot.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the return policy?",
    "store_id": "NY_001"
  }'

# Expected: Normal RAG response with "is_safety_response": false

# Test safety concern (DO NOT test with real crisis messages)
curl -X POST https://$PROJECT_ID.uc.r.appspot.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I am feeling stressed",
    "store_id": "NY_001",
    "user_id": "test_user"
  }'

# Expected: Safety response with resources and "is_safety_response": true
```

---

## Monitoring & Alerts Setup

### 1. Set Up Cloud Logging Alerts

Create an alert for critical safety escalations:

```bash
# Create notification channel (email)
gcloud alpha monitoring channels create \
  --display-name="Security Team Alerts" \
  --type=email \
  --channel-labels=email_address=security@your-company.com \
  --project=$PROJECT_ID

# Get the channel ID
CHANNEL_ID=$(gcloud alpha monitoring channels list --project=$PROJECT_ID \
  --filter="displayName='Security Team Alerts'" \
  --format="value(name)")

# Create alert policy for critical escalations
cat > alert-policy.yaml << EOF
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
  - $CHANNEL_ID
alertStrategy:
  autoClose: 3600s
EOF

gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml --project=$PROJECT_ID
```

### 2. Set Up Pub/Sub Monitoring

Monitor Pub/Sub subscription backlog:

```bash
# Create alert for unacknowledged messages
cat > pubsub-alert.yaml << EOF
displayName: "Safety Alert Backlog"
conditions:
  - displayName: "Unacknowledged safety alerts"
    conditionThreshold:
      filter: |
        resource.type="pubsub_subscription"
        resource.label.subscription_id=~".*safety.*"
        metric.type="pubsub.googleapis.com/subscription/num_undelivered_messages"
      comparison: COMPARISON_GT
      thresholdValue: 5
      duration: 300s
notificationChannels:
  - $CHANNEL_ID
EOF

gcloud alpha monitoring policies create --policy-from-file=pubsub-alert.yaml --project=$PROJECT_ID
```

---

## Post-Deployment Checklist

After deploying the safety framework:

- [ ] **Verify Pub/Sub topics created**
  ```bash
  gcloud pubsub topics list --project=$PROJECT_ID | grep safety
  ```

- [ ] **Verify subscriptions created**
  ```bash
  gcloud pubsub subscriptions list --project=$PROJECT_ID | grep safety
  ```

- [ ] **Verify encryption key stored**
  ```bash
  gcloud secrets versions access latest --secret=safety-encryption-key --project=$PROJECT_ID
  ```

- [ ] **Verify Firestore rules deployed**
  ```bash
  gcloud firestore rules list --project=$PROJECT_ID
  ```

- [ ] **Test API endpoint responds**
  ```bash
  curl https://$PROJECT_ID.uc.r.appspot.com/health
  ```

- [ ] **Test safe question classification**
  ```bash
  curl -X POST https://$PROJECT_ID.uc.r.appspot.com/ask -d '{"question":"What is the return policy?"}'
  ```

- [ ] **Verify support resource phone numbers are correct**
  - Check `backend/safety/config.py`
  - Test calling each number

- [ ] **Train HR/Security teams**
  - How to access Pub/Sub messages
  - How to retrieve Firestore reports
  - Escalation protocols

- [ ] **Set up monitoring dashboard**
  - Cloud Logging for classifications
  - Pub/Sub metrics
  - Firestore usage

- [ ] **Document incident response procedures**
  - Who to contact for each priority level
  - Response time SLAs
  - Escalation paths

---

## Troubleshooting

### Issue: "Permission denied" when accessing Secret Manager

**Solution**:
```bash
# Verify service account has access
gcloud secrets get-iam-policy safety-encryption-key --project=$PROJECT_ID

# If missing, grant access
gcloud secrets add-iam-policy-binding safety-encryption-key \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID
```

### Issue: "Firestore permission denied"

**Solution**:
```bash
# Grant Firestore access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Issue: Reports not being created

**Check**:
1. Firestore database exists
2. Service account has datastore.user role
3. Firestore security rules allow service account to write
4. Check Cloud Logging for errors

### Issue: Pub/Sub messages not being received

**Check**:
1. Topics exist
2. Subscriptions exist and are pointing to correct topics
3. Service account has pubsub.publisher role
4. Check subscription pull to see if messages are queued

---

## Cost Estimates

### Safety Framework Additional Costs

- **Firestore**: ~$0.01 per 10,000 report writes (estimate: $1-5/month)
- **Pub/Sub**: ~$0.06 per 1M messages (estimate: $1-2/month)
- **Secret Manager**: ~$0.06 per secret per month (estimate: $0.06/month)
- **Cloud Logging**: Included in App Engine pricing
- **Vertex AI (LLM)**: ~$0.0005 per message if LLM enabled (estimate: $10-50/month depending on volume)

**Total Additional Cost**: ~$12-57/month (depending on message volume and LLM usage)

**Cost Savings**:
- Set `SAFETY_LLM_ENABLED=false` to use pattern-only detection (saves ~$10-50/month)
- Use shorter retention periods to reduce Firestore storage costs

---

## Maintenance

### Weekly Tasks
- Review critical escalations in Cloud Logging
- Check Pub/Sub subscription backlogs
- Verify all support resource phone numbers working

### Monthly Tasks
- Review classification accuracy (false positives/negatives)
- Update detection patterns if needed
- Review and acknowledge Pub/Sub messages
- Audit Firestore access logs

### Quarterly Tasks
- Rotate encryption key in Secret Manager
- Review and update Firestore security rules
- Conduct staff training refresher
- Compliance audit

### Annual Tasks
- Update all support resource phone numbers
- Review and update response templates
- Security audit
- Privacy compliance review

---

## Additional Resources

- [SAFETY_FRAMEWORK.md](SAFETY_FRAMEWORK.md) - Complete framework documentation
- [SAFETY_QUICKSTART.md](SAFETY_QUICKSTART.md) - Quick setup guide
- [SAFETY_IMPLEMENTATION_SUMMARY.md](SAFETY_IMPLEMENTATION_SUMMARY.md) - Implementation details
- [tests/test_safety.py](tests/test_safety.py) - Test suite

---

**Version**: 1.0.0
**Last Updated**: 2026-01-09
**Deployment Status**: Ready for Production
