import streamlit as st
import requests
from pathlib import Path
import tempfile
import os
import uuid

# API URL configuration - checks Streamlit secrets first, then environment variable, then defaults to localhost
try:
    API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "http://127.0.0.1:8000"))
except Exception:
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Generate session ID for tracking
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Store last Q&A for feedback
if 'last_question' not in st.session_state:
    st.session_state.last_question = None
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None

# Store question history
if 'question_history' not in st.session_state:
    st.session_state.question_history = []

# Store safety features status
if 'safety_features' not in st.session_state:
    st.session_state.safety_features = {}

st.set_page_config(
    page_title="Retail Intelligence Assistant",
    layout="wide",
)

# ---------------- Sidebar ----------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Macy%27s_Logo.svg", width=160)
st.sidebar.title("Retail RAG Control Panel")

# Fetch and display safety features status
try:
    health_response = requests.get(f"{API_URL}/health", timeout=5)
    if health_response.status_code == 200:
        health_data = health_response.json()
        st.session_state.safety_features = health_data.get("safety_features", {})
except:
    pass

# AI Safety Status Panel
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ AI SAFETY STATUS")

safety_features = st.session_state.safety_features
if safety_features:
    features = [
        ("Document Safety Verification", safety_features.get("document_verification", False)),
        ("Prompt Injection Protection", safety_features.get("prompt_injection_protection", False)),
        ("OWASP LLM Guardrails", safety_features.get("owasp_llm_guardrails", False)),
        ("Response Safety Filter", safety_features.get("response_safety_filter", False)),
        ("Confidential Escalation", safety_features.get("confidential_escalation", False))
    ]

    for feature_name, enabled in features:
        status_icon = "✅" if enabled else "❌"
        st.sidebar.markdown(f"{status_icon} **{feature_name}:** {'ON' if enabled else 'OFF'}")
else:
    st.sidebar.info("Connecting to backend...")

st.sidebar.markdown("---")

store_id = st.sidebar.selectbox(
    "Select Store",
    ["NY_001", "CA_023", "TX_104"]
)

uploaded_files = st.sidebar.file_uploader(
    "Upload Knowledge Base Files",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if st.sidebar.button("Ingest Files"):
    if not uploaded_files:
        st.sidebar.warning("Please upload at least one document.")
    else:
        with st.spinner("Verifying and indexing documents..."):
            try:
                for file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp:
                        tmp.write(file.read())
                        tmp_path = tmp.name

                    response = requests.post(
                        f"{API_URL}/ingest",
                        files={"file": open(tmp_path, "rb")},
                        data={"store_id": store_id},
                        timeout=60
                    )

                    if response.status_code != 200:
                        st.sidebar.error(f"Failed to ingest {file.name}")
                        continue

                    result = response.json()

                    # Display document verification status
                    if result.get("status") == "blocked":
                        st.sidebar.error(f"❌ **{file.name}** - REJECTED")
                        st.sidebar.caption(f"Reason: {result.get('summary', 'Unsafe content detected')}")
                    elif result.get("status") == "indexed":
                        verification = result.get("verification", {})
                        severity = verification.get("severity", "none")

                        if severity == "medium":
                            st.sidebar.warning(f"⚠️ **{file.name}** - QUARANTINED")
                            st.sidebar.caption("Document flagged for review")
                        else:
                            st.sidebar.success(f"✔️ **{file.name}** - VERIFIED")
                            st.sidebar.caption(f"Safe for AI use ({result.get('chunks', 0)} chunks)")

                os.remove(tmp_path)

            except requests.exceptions.ConnectionError:
                st.sidebar.error(f"Cannot connect to backend at {API_URL}. Please configure API_URL.")
            except Exception as e:
                st.sidebar.error(f"Error ingesting files: {str(e)}")

# ---------------- Feedback Stats (Admin) ----------------
st.sidebar.markdown("---")
with st.sidebar.expander("📊 Feedback Statistics"):
    if st.button("Refresh Stats", key="refresh_stats"):
        try:
            stats_response = requests.get(f"{API_URL}/feedback/stats")
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                if stats_data.get("status") == "success":
                    stats = stats_data["stats"]
                    st.metric("Total Responses", stats["total_responses"])
                    st.metric("Average Rating", f"{stats['average_rating']}/5.0")
                    st.metric("Helpful %", f"{stats['helpful_percentage']}%")
                    st.metric("Comments", stats["total_comments"])

                    if stats["total_responses"] > 0:
                        st.markdown("**Rating Distribution:**")
                        dist = stats["rating_distribution"]
                        for rating in [5, 4, 3, 2, 1]:
                            count = dist.get(str(rating), 0)
                            bar = "█" * count
                            st.text(f"{'⭐' * rating} {bar} ({count})")
                else:
                    st.warning("Could not load stats")
            else:
                st.error("Failed to load stats")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ---------------- Question History ----------------
st.sidebar.markdown("---")
with st.sidebar.expander("📜 Recent Questions", expanded=False):
    if st.session_state.question_history:
        st.markdown("*Click a question to ask it again*")
        st.markdown("")

        recent_questions = st.session_state.question_history[-10:][::-1]

        for idx, q_data in enumerate(recent_questions):
            question_text = q_data['question']
            timestamp = q_data['timestamp']

            display_text = question_text if len(question_text) <= 60 else question_text[:57] + "..."

            if st.button(
                f"🔄 {display_text}",
                key=f"history_{idx}",
                help=f"Asked at {timestamp}\n\n{question_text}",
                use_container_width=True
            ):
                st.session_state.reuse_question = question_text
                st.rerun()

        st.markdown("")
        if st.button("🗑️ Clear History", use_container_width=True, key="clear_history"):
            st.session_state.question_history = []
            st.rerun()
    else:
        st.info("No questions asked yet")

# ---------------- Main UI ----------------
st.title("🛍️ Retail Knowledge Assistant")
st.markdown("Ask operational or technical questions about store issues, SOPs, or inventory.")

# Check if we need to reuse a question from history
default_question = ""
if 'reuse_question' in st.session_state and st.session_state.reuse_question:
    default_question = st.session_state.reuse_question
    st.session_state.reuse_question = None

question = st.text_input("Enter your question", value=default_question)

if st.button("Ask"):
    if not question:
        st.warning("Please enter a question first.")
        st.stop()

    with st.spinner("Analyzing knowledge base..."):
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question, "store_id": store_id},
                timeout=30
            )

            if response.status_code != 200:
                st.error("Backend error. Please try again.")
                st.stop()

            res = response.json()
        except requests.exceptions.ConnectionError:
            st.error(f"""
            **Cannot connect to backend API**

            The frontend cannot reach the backend service at: `{API_URL}`

            **If you're on Streamlit Cloud:**
            1. Go to your app settings (⚙️)
            2. Click "Secrets" in the left sidebar
            3. Add your backend URL:
            ```
            API_URL = "https://your-backend-service.run.app"
            ```

            **Backend URL should be your Cloud Run service URL, not localhost.**
            """)
            st.stop()
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            st.stop()
        except Exception as e:
            st.error(f"Error connecting to backend: {str(e)}")
            st.stop()

        # Store Q&A for feedback
        st.session_state.last_question = question
        st.session_state.last_answer = res["answer"]

        # Add question to history
        from datetime import datetime
        question_entry = {
            'question': question,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'store_id': store_id
        }

        if not st.session_state.question_history or \
           st.session_state.question_history[-1]['question'] != question:
            st.session_state.question_history.append(question_entry)

    # Response Safety Indicator
    response_safety = res.get("response_safety", {})
    safety_status = response_safety.get("status", "unknown")
    safety_reason = response_safety.get("reason", "No safety information")

    st.markdown("---")

    # Safety status badge
    if safety_status == "passed":
        st.success(f"✔️ **Response Safety Check:** PASSED - {safety_reason}")
    elif safety_status == "modified":
        st.warning(f"⚠️ **Response Safety Check:** MODIFIED - {safety_reason}")
    elif safety_status == "blocked":
        st.error(f"❌ **Response Safety Check:** BLOCKED - {safety_reason}")
    else:
        st.info(f"ℹ️ **Response Safety Check:** {safety_status.upper()}")

    st.markdown("---")

    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("Answer")

        # Check if this is a safety response (mental health, etc.)
        if res.get("is_safety_response", False):
            st.info(res["answer"])

            # Display support resources if available
            if "support_resources" in res and res["support_resources"]:
                st.markdown("### 📞 Support Resources")
                for resource in res["support_resources"]:
                    with st.expander(f"{resource['name']}"):
                        st.markdown(f"**Contact:** {resource['contact']}")
                        if resource.get('hours'):
                            st.markdown(f"**Hours:** {resource['hours']}")
                        if resource.get('description'):
                            st.markdown(resource['description'])
        else:
            st.success(res["answer"])

    with col2:
        st.subheader("📎 Citations")
        citations = res.get("citations", [])
        if citations:
            for c in citations:
                with st.expander(f"[{c['id']}] {c['source']} — Store {c['store_id']}"):
                    st.write(c["snippet"])
        else:
            st.caption("No citations available")

    # ---------------- Feedback Section ----------------
    st.markdown("---")
    st.subheader("💬 Was this answer helpful?")
    st.markdown("*Your feedback helps us improve the knowledge assistant*")

    feedback_col1, feedback_col2 = st.columns([1, 2])

    with feedback_col1:
        st.markdown("**Rate the answer quality:**")
        rating = st.radio(
            "Rating",
            options=[5, 4, 3, 2, 1],
            format_func=lambda x: "⭐" * x,
            horizontal=True,
            label_visibility="collapsed",
            key="rating_input"
        )

        was_helpful = st.radio(
            "Was this helpful in answering your query?",
            options=[True, False],
            format_func=lambda x: "👍 Yes" if x else "👎 No",
            horizontal=True,
            key="helpful_input"
        )

    with feedback_col2:
        comment = st.text_area(
            "Additional feedback (optional):",
            placeholder="Tell us how we can improve this answer...",
            height=100,
            key="comment_input"
        )

    if st.button("Submit Feedback", type="primary", use_container_width=False):
        feedback_data = {
            "question": st.session_state.last_question,
            "answer": st.session_state.last_answer,
            "rating": rating,
            "was_helpful": was_helpful,
            "comment": comment if comment else None,
            "store_id": store_id,
            "session_id": st.session_state.session_id
        }

        try:
            feedback_response = requests.post(f"{API_URL}/feedback", json=feedback_data)

            if feedback_response.status_code == 200:
                result = feedback_response.json()
                if result.get("status") == "success":
                    st.success("✅ Thank you for your feedback!")
                else:
                    st.warning(f"⚠️ {result.get('message', 'Could not save feedback')}")
            else:
                st.error("Failed to submit feedback. Please try again.")
        except Exception as e:
            st.error(f"Error submitting feedback: {str(e)}")
