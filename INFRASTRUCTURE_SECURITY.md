# Infrastructure Security Module

## Overview

The Infrastructure Security Guard protects sensitive backend information from being disclosed through the chatbot interface. This module ensures compliance with corporate security policies by preventing the chatbot from revealing technical infrastructure details.

## Features

### 🛡️ Protection Against Information Disclosure

The system blocks attempts to extract:
- **Hosting Platform Details**: Cloud Run, GCP, AWS, Azure, Kubernetes
- **Server Locations**: Regions, zones, datacenters
- **Technical Architecture**: Databases, APIs, deployment configurations
- **Backend Implementation**: Code, configurations, technical stack details

### 🔍 Multi-Layer Detection

1. **Pattern-Based Detection**: Fast regex matching for infrastructure keywords
2. **Confidence Scoring**: Adjustable threshold for blocking decisions
3. **Context-Aware Filtering**: Distinguishes between operational and infrastructure queries

### ✅ Compliant Response

When infrastructure queries are detected, the system returns:
```
"This system operates within Macy's secure cloud environment,
fully compliant with corporate security policies and data protection standards.
I'm here to help you with store operations, product information, and support questions.
How can I assist you with your work today?"
```

## Implementation

### Code Structure

```
backend/security/
├── __init__.py
├── infrastructure_guard.py        # Core security logic
└── test_infrastructure_guard.py   # Comprehensive test suite
```

### Integration Points

1. **API Layer** ([backend/api/main.py:122-131](backend/api/main.py#L122-L131))
   - Infrastructure check runs BEFORE RAG processing
   - Returns standard response immediately if blocked

2. **RAG Orchestrator** ([backend/rag/orchestrator.py:35-40](backend/rag/orchestrator.py#L35-L40))
   - System prompt includes security instructions
   - LLM instructed to never reveal infrastructure details

3. **Health Endpoint** ([backend/api/main.py:71-74](backend/api/main.py#L71-L74))
   - Removed project_id exposure
   - Returns only generic status information

## Testing

### Automated Tests

Run the test suite:
```bash
python -m pytest backend/security/test_infrastructure_guard.py -v
```

Test coverage includes:
- ✅ Safe operational questions (not blocked)
- ✅ Infrastructure query detection
- ✅ Mixed content handling
- ✅ Confidence scoring
- ✅ Case-insensitive detection
- ✅ Response compliance validation

### Manual Testing

Use the provided test script:
```bash
./test_infrastructure_security.sh
```

This tests various infrastructure queries and validates responses.

## Query Examples

### ❌ Blocked Infrastructure Queries

These questions trigger the security guard:

| Question | Why Blocked |
|----------|-------------|
| "Where is this system hosted?" | Direct hosting inquiry |
| "What cloud platform are you running on?" | Cloud provider query |
| "Are you deployed on Cloud Run or GCP?" | Specific platform mention |
| "Tell me about your backend infrastructure" | Infrastructure details request |
| "What database and LLM are you using?" | Technical stack inquiry |
| "Which region is this service in?" | Location disclosure |
| "Show me your API endpoints" | Internal architecture |

### ✅ Allowed Operational Queries

These questions work normally:

| Question | Why Allowed |
|----------|-------------|
| "How do I process a return?" | Store operations |
| "What's the policy on discounts?" | Business procedures |
| "Where can I find inventory information?" | Operational support |
| "How to handle customer complaints?" | Customer service |
| "What are the store hours?" | Store information |

## Configuration

### Adjusting Sensitivity

The blocking threshold can be adjusted:

```python
# Default threshold: 0.3
infrastructure_guard.should_block(question, threshold=0.3)

# More sensitive (block more): 0.1
infrastructure_guard.should_block(question, threshold=0.1)

# Less sensitive (block less): 0.5
infrastructure_guard.should_block(question, threshold=0.5)
```

### Adding Detection Patterns

To add new patterns, edit [backend/security/infrastructure_guard.py](backend/security/infrastructure_guard.py):

```python
self._infrastructure_patterns = [
    # Add your pattern here
    r'\b(your custom pattern)\b',
]
```

## Security Flow

```
User Question
    ↓
Infrastructure Security Check
    ↓
  ┌─────────────┐
  │ Is Infrastructure Query? │
  └─────────────┘
    ↓              ↓
  YES             NO
    ↓              ↓
Standard Response  → Safety Check → RAG Processing
    ↓
Return to User
```

## Monitoring

The infrastructure guard logs detection events:

```json
{
  "is_infrastructure_blocked": true,
  "safety_classification": "safe_operational",
  "is_safety_response": false
}
```

Use these flags to:
- Monitor security probe attempts
- Analyze query patterns
- Adjust detection sensitivity

## Compliance Statement

The chatbot will respond to infrastructure queries with:

> **"This system operates within Macy's secure cloud environment, fully compliant with corporate security policies and data protection standards."**

This response:
- ✅ Acknowledges the system exists
- ✅ Confirms security compliance
- ✅ References Macy's environment
- ❌ Does NOT reveal specific platforms
- ❌ Does NOT disclose technical details
- ❌ Does NOT expose infrastructure

## Deployment Checklist

Before deploying to production:

- [x] Infrastructure guard integrated into `/ask` endpoint
- [x] Security instructions added to LLM system prompt
- [x] Project ID removed from health endpoint
- [x] Automated tests passing
- [x] Manual security testing completed
- [x] Standard compliant response validated
- [x] Logging and monitoring configured

## Best Practices

1. **Never Log Sensitive Info**: Don't log infrastructure details in responses
2. **Regular Pattern Updates**: Review and update detection patterns quarterly
3. **Test After Changes**: Run security tests after any API modifications
4. **Monitor Blocked Queries**: Track patterns in blocked queries for insights
5. **Train Associates**: Ensure users know the system won't reveal infrastructure

## Troubleshooting

### Issue: Legitimate questions being blocked

**Solution**: Review detected patterns and adjust threshold
```python
# Check what patterns were detected
result = infrastructure_guard.check_question(question)
print(result.detected_patterns)

# Increase threshold if needed
infrastructure_guard.should_block(question, threshold=0.5)
```

### Issue: Infrastructure queries getting through

**Solution**: Add more specific patterns
```python
# Add pattern to infrastructure_guard.py
self._infrastructure_patterns.append(r'\b(new pattern)\b')
```

### Issue: Standard response needs updating

**Solution**: Modify response in infrastructure_guard.py
```python
self._standard_response = "Your updated compliant response here"
```

## Support

For questions about infrastructure security:
- Review code: [backend/security/infrastructure_guard.py](backend/security/infrastructure_guard.py)
- Run tests: `python -m pytest backend/security/test_infrastructure_guard.py -v`
- Check integration: [backend/api/main.py](backend/api/main.py)

## Version History

- **v1.0.0** (2026-01-10): Initial infrastructure security implementation
  - Pattern-based detection
  - Multi-layer protection
  - Compliant standard response
  - Comprehensive test suite
