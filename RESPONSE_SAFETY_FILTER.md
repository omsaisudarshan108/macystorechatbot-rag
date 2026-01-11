# Response Safety Filter

Post-generation safety enforcement for RAG outputs.

---

## Overview

The Response Safety Filter is a **post-generation** safety layer that checks LLM-generated responses AFTER they are created by the RAG system but BEFORE they are shown to users.

This ensures that even if malicious content bypasses document verification or is synthesized during generation, it cannot reach end users.

---

## Safety Checks

### 1. Hallucination Detection

**Purpose:** Ensure responses are grounded in verified documents

**How it works:**
- Extracts key phrases from response
- Compares with retrieved context documents
- Calculates overlap ratio
- Flags if overlap < 20%

**Example:**
```
Question: "What is the admin password?"
Context: [Documents about store hours, return policy]
Response: "The admin password is admin123"

✅ BLOCKED - Insufficient verified information
```

### 2. Malicious Intent Detection

**Purpose:** Block responses containing harmful instructions

**Patterns detected:**
- System exploitation attempts
- Security bypass instructions
- Credential theft guidance
- Policy override commands

**Example:**
```
Response: "You can hack the system by..."

✅ BLOCKED - Security policy triggered
```

### 3. Profanity Detection

**Purpose:** Ensure professional communication

**Action:** MODIFY (clean response)

**Example:**
```
Original: "This f***ing system is broken"
Modified: "This [removed] system is broken"

⚠️ MODIFIED - Response modified to meet safety standards
```

### 4. Violence Detection

**Purpose:** Block harmful content

**Patterns detected:**
- Threats of violence
- Instructions for harm
- Dangerous weapon information

**Action:** BLOCK

### 5. Self-Harm Detection

**Purpose:** Protect vulnerable users

**Patterns detected:**
- Suicide references
- Self-injury content
- Crisis language

**Action:** BLOCK + Special messaging

**Example:**
```
✅ BLOCKED - Please contact Employee Assistance Program
```

### 6. Hate Speech Detection

**Purpose:** Prevent discrimination

**Patterns detected:**
- Discriminatory language
- Hate group references
- Bigotry

**Action:** MODIFY or BLOCK

### 7. Political Unsafe Content

**Purpose:** Maintain neutrality

**Patterns detected:**
- Political advocacy
- Partisan statements
- Voting guidance

**Action:** MODIFY

---

## Safety Actions

### PASS
- Response is safe and grounded
- No modifications needed
- Full response delivered to user

**UI Display:**
```
✔️ Response Safety Check: PASSED
Reason: Response passed all safety checks
```

### MODIFY
- Response contains minor violations
- Content is cleaned/sanitized
- Modified response delivered

**UI Display:**
```
⚠️ Response Safety Check: MODIFIED
Reason: Response modified to meet safety standards
```

**Note added to response:**
```
[Note: Response was modified to meet safety policies]
```

### BLOCK
- Response contains critical violations
- No response delivered
- Safe fallback message shown

**UI Display:**
```
❌ Response Safety Check: BLOCKED
Reason: Safety policy triggered
```

**Default safe response:**
```
"I cannot provide that information due to safety policies.
Please contact your supervisor or Macy's support for assistance."
```

---

## Integration Architecture

```
┌─────────────────────────────────────────┐
│  User Question                          │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Pre-Processing Safety                  │
│  - Infrastructure Guard                 │
│  - Safety Classifier                    │
│  - Policy Engine                        │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  RAG Orchestrator                       │
│  - Hybrid Retrieval (Chroma + BM25)    │
│  - Reranking (Cross-Encoder)           │
│  - LLM Generation (Vertex AI Gemini)   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Response Safety Filter ◄───── NEW      │
│  - Hallucination Check                  │
│  - Malicious Intent Check               │
│  - Profanity Check                      │
│  - Violence/Self-Harm Check             │
│  - Hate Speech Check                    │
│  - Political Content Check              │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Safe Response to User                  │
└─────────────────────────────────────────┘
```

---

## Implementation Details

### Backend Integration

**File:** `backend/api/main.py`

```python
from backend.safety.response_filter import ResponseSafetyFilter, SafetyAction

# Initialize filter
response_filter = ResponseSafetyFilter()

# In /ask endpoint, after RAG generation:
safety_check = response_filter.check_response_safety(
    response=rag_response.get("answer", ""),
    context_docs=context_docs,
    question=query.question
)

# Apply action
if safety_check.action == SafetyAction.BLOCK:
    return blocked_response
elif safety_check.action == SafetyAction.MODIFY:
    return modified_response
else:
    return original_response
```

### UI Integration

**File:** `ui/app.py`

```python
# Extract safety check result
response_safety = res.get("response_safety", {})
safety_status = response_safety.get("status", "unknown")

# Display safety indicator
if safety_status == "passed":
    st.success("✔️ Response Safety Check: PASSED")
elif safety_status == "modified":
    st.warning("⚠️ Response Safety Check: MODIFIED")
elif safety_status == "blocked":
    st.error("❌ Response Safety Check: BLOCKED")
```

---

## Configuration

### Pattern Customization

**File:** `backend/safety/response_filter.py`

```python
def _init_patterns(self):
    # Add custom patterns for your organization
    self.profanity_patterns = [
        r'\b(custom|pattern|here)\b',
        # ... more patterns
    ]
```

### Severity Thresholds

```python
# Block if overlap ratio < threshold
HALLUCINATION_THRESHOLD = 0.2  # Default: 20%

# Modify: criteria for adjusting response
def _determine_action(self, violations):
    if SafetyViolation.SELF_HARM in violations:
        return SafetyAction.BLOCK  # Always block
    # ... custom logic
```

---

## Testing

### Unit Tests

```bash
# Run response filter tests
pytest backend/safety/test_response_filter.py -v
```

### Integration Tests

```bash
# Test hallucination detection
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the secret password?", "store_id": "TEST"}'

# Expected: BLOCKED with hallucination reason
```

### Live Testing

1. **Upload clean documents**
2. **Ask question with no context match**
3. **Verify BLOCKED response**
4. **Check logs for hallucination detection**

---

## Monitoring

### Backend Logs

**Safety events logged:**
```
INFO: Response safety check: PASSED (confidence: 0.95)
WARNING: Response modified: profanity detected
ERROR: Response blocked: hallucination detected
```

### Metrics

Track in production:
- Pass rate: % of responses that pass safety
- Modify rate: % of responses modified
- Block rate: % of responses blocked
- Violation distribution by category

---

## User-Friendly Messaging

The filter NEVER reveals detection logic to users.

**Internal:** "hallucination detected"
**User sees:** "Insufficient verified information"

**Internal:** "malicious_intent detected"
**User sees:** "Security policy triggered"

**Internal:** "self_harm detected"
**User sees:** "Please contact Employee Assistance Program"

---

## Compliance

### OWASP LLM Top 10

✅ **LLM01: Prompt Injection** - Filtered via pattern detection
✅ **LLM02: Insecure Output Handling** - All responses sanitized
✅ **LLM06: Sensitive Information Disclosure** - Hallucination prevention
✅ **LLM07: Insecure Plugin Design** - N/A
✅ **LLM09: Overreliance** - Low-confidence responses blocked

### Responsible AI

✅ **Harm Prevention** - Violence/self-harm detection
✅ **Fairness** - Hate speech detection
✅ **Transparency** - Safety indicators visible to users
✅ **Privacy** - No logging of blocked content verbatim

---

## Limitations

### Known Edge Cases

1. **Obfuscated Content**
   - Filter uses regex patterns
   - Creative spelling may bypass (e.g., "f.u.c.k")
   - Mitigation: Regular pattern updates

2. **Context-Dependent Language**
   - Some professional terms may trigger false positives
   - Example: "kill process" in technical context
   - Mitigation: Context-aware pattern matching

3. **Multilingual Content**
   - Current patterns are English-only
   - Non-English malicious content may pass
   - Mitigation: Add language-specific patterns

### Performance Impact

- **Latency:** +50-150ms per response
- **Memory:** Minimal (patterns pre-compiled)
- **Scalability:** Stateless, horizontally scalable

---

## Future Enhancements

1. **LLM-Based Classification**
   - Use smaller LLM for semantic safety checks
   - Higher accuracy than regex patterns
   - Tradeoff: Increased latency

2. **Confidence Scoring**
   - Multi-level confidence thresholds
   - CRITICAL (block), HIGH (warn), MEDIUM (log)

3. **User Feedback Loop**
   - Allow users to flag false positives
   - Improve pattern accuracy over time

4. **Custom Safety Policies**
   - Per-store or per-role safety rules
   - Fine-grained control over blocking logic

---

## Support

For issues or questions:
- GitHub Issues: [Link to repository]
- Internal: Contact AI Platform Team
- Escalation: See [SAFETY_FRAMEWORK.md](SAFETY_FRAMEWORK.md)

---

**Last Updated:** 2026-01-10
**Module Version:** 1.0.0
