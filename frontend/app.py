import streamlit as st
import requests
import json
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────────

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="JurisMind — Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
    }

    /* Main background */
    .stApp {
        background: #0d1117;
        color: #e6edf3;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #161b22 !important;
        border-right: 1px solid #30363d;
    }

    /* Title */
    .jurismind-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #c9a84c;
        letter-spacing: -0.5px;
        margin-bottom: 0;
    }
    .jurismind-sub {
        color: #8b949e;
        font-size: 0.9rem;
        margin-top: 4px;
    }

    /* Chat messages */
    .user-msg {
        background: #1c2128;
        border: 1px solid #30363d;
        border-radius: 12px 12px 0 12px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        color: #e6edf3;
    }
    .bot-msg {
        background: #161b22;
        border: 1px solid #c9a84c33;
        border-left: 3px solid #c9a84c;
        border-radius: 0 12px 12px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 85%;
        color: #e6edf3;
    }
    .msg-meta {
        font-size: 0.72rem;
        color: #484f58;
        margin-top: 4px;
    }
    .source-badge-kbs {
        background: #1f4e3d;
        color: #3fb950;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .source-badge-groq {
        background: #1c2e5a;
        color: #58a6ff;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .source-badge-greeting {
        background: #2d2d0f;
        color: #e3b341;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    /* Prediction result cards */
    .pred-card {
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #30363d;
    }
    .pred-win  { background: #0d2818; border-color: #3fb950; }
    .pred-lose { background: #2d0f0f; border-color: #f85149; }
    .pred-uncertain { background: #2d1f0a; border-color: #e3b341; }

    /* Progress bar custom */
    .conf-bar-container {
        background: #21262d;
        border-radius: 6px;
        height: 10px;
        margin: 6px 0;
        overflow: hidden;
    }
    .conf-bar-fill-green { background: #3fb950; height: 10px; border-radius: 6px; }
    .conf-bar-fill-red   { background: #f85149; height: 10px; border-radius: 6px; }
    .conf-bar-fill-orange{ background: #e3b341; height: 10px; border-radius: 6px; }

    /* Divider */
    hr { border-color: #30363d; }

    /* Input */
    .stTextInput > div > input, .stTextArea > div > textarea {
        background: #161b22 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background: #c9a84c !important;
        color: #0d1117 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
    }
    .stButton > button:hover {
        background: #e0be6a !important;
    }

    /* Disclaimer */
    .disclaimer {
        background: #2d1f0a;
        border: 1px solid #e3b341;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #e3b341;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "page" not in st.session_state:
    st.session_state.page = "Chat"


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<p class="jurismind-title">⚖️ JurisMind</p>', unsafe_allow_html=True)
    st.markdown('<p class="jurismind-sub">AI Legal Assistant — DOJ</p>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["💬 Chat", "🔮 Case Outcome Predictor", "📚 Knowledge Base", "ℹ️ About"],
        key="nav"
    )

    st.markdown("---")
    st.markdown("**Quick Topics**")
    quick_topics = {
        "📁 eFiling Help": "How do I e-file a case?",
        "💳 Court Fee Payment": "How do I pay court fees online?",
        "⚖️ Legal Aid": "How can I get free legal aid?",
        "📋 Case Status": "How do I check my case status?",
        "🚨 File FIR": "How do I file an FIR?",
        "🔓 Bail Process": "How does the bail process work?",
    }

    for label, query in quick_topics.items():
        if st.button(label, use_container_width=True):
            st.session_state.quick_query = query

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown('<p style="color:#484f58; font-size:0.75rem; margin-top:20px;">Powered by FastAPI + Groq + scikit-learn</p>', unsafe_allow_html=True)


# ─── Helper Functions ──────────────────────────────────────────────────────────

def send_chat(message: str):
    try:
        resp = requests.post(f"{API_URL}/chat", json={"message": message}, timeout=15)
        return resp.json()
    except Exception as e:
        return {"reply": f"⚠️ Cannot connect to backend. Make sure the API is running.\n\nError: {e}", "intent": "error", "source": "error"}


def send_predict(case_desc: str):
    try:
        resp = requests.post(f"{API_URL}/predict", json={"case_description": case_desc}, timeout=15)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def source_badge(source: str) -> str:
    badges = {
        "kbs": '<span class="source-badge-kbs">📚 Knowledge Base</span>',
        "groq": '<span class="source-badge-groq">🤖 AI Generated</span>',
        "greeting": '<span class="source-badge-greeting">👋 System</span>',
        "system": '<span class="source-badge-greeting">⚙️ System</span>',
        "error": '<span class="source-badge-groq">⚠️ Error</span>',
    }
    return badges.get(source, f'<span class="source-badge-groq">{source}</span>')


# ─── Pages ─────────────────────────────────────────────────────────────────────

# ── 1. CHAT PAGE ──
if page == "💬 Chat":
    st.markdown("## 💬 Legal Assistance Chat")
    st.markdown("Ask me about **eFiling**, **court fees**, **legal aid**, **case procedures**, and more.")
    st.markdown("---")

    # Handle quick topic clicks - auto send
    if "quick_query" in st.session_state:
        quick_msg = st.session_state.quick_query
        del st.session_state.quick_query
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            "role": "user",
            "content": quick_msg,
            "time": now
        })
        with st.spinner("JurisMind is thinking..."):
            result = send_chat(quick_msg)
        st.session_state.chat_history.append({
            "role": "bot",
            "content": result.get("reply", "Sorry, I couldn't process that."),
            "source": result.get("source", "groq"),
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()

    # Display chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="bot-msg">
                👋 Hello! I'm <strong>JurisMind</strong>, your AI legal assistant for Department of Justice services.<br><br>
                I can help you with:<br>
                • 📁 <strong>eFiling</strong> — file cases online<br>
                • 💳 <strong>ePay</strong> — court fee payments<br>
                • ⚖️ <strong>Legal Aid</strong> — free legal assistance<br>
                • 📋 <strong>Court Info</strong> — timings, case status, jurisdiction<br>
                • 📖 <strong>Legal FAQs</strong> — FIR, bail, divorce, consumer rights<br><br>
                How can I assist you today?
            </div>
            """, unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg">🧑 {msg["content"]}<br><span class="msg-meta">{msg["time"]}</span></div>', unsafe_allow_html=True)
            else:
                badge = source_badge(msg.get("source", "groq"))
                st.markdown(f'<div class="bot-msg">⚖️ {msg["content"]}<br><span class="msg-meta">{msg["time"]} &nbsp; {badge}</span></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Input form - Enter key + button both work
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Your question",
                placeholder="e.g. How do I file a case online?",
                label_visibility="collapsed",
                key="chat_input"
            )
        with col2:
            send_btn = st.form_submit_button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": now
        })
        with st.spinner("JurisMind is thinking..."):
            result = send_chat(user_input)
        st.session_state.chat_history.append({
            "role": "bot",
            "content": result.get("reply", "Sorry, I couldn't process that."),
            "source": result.get("source", "groq"),
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()

   


# ── 2. CASE OUTCOME PREDICTOR ──
elif page == "🔮 Case Outcome Predictor":
    st.markdown("## 🔮 Case Outcome Predictor")
    st.markdown("Describe your case in detail and our ML model will predict the likely outcome with a confidence score.")

    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Disclaimer:</strong> This prediction is generated by a Machine Learning model trained on case patterns.
        It is NOT legal advice and should NOT replace consultation with a qualified lawyer.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Example descriptions
    with st.expander("📌 See example descriptions"):
        st.markdown("""
        **Civil/Win Example:**
        *"Plaintiff filed for breach of contract. We have a signed agreement, payment records, and WhatsApp messages proving non-delivery. Two independent witnesses are available."*

        **Criminal/Acquittal Example:**
        *"Accused is charged with theft but the only evidence is a single eyewitness who is related to the complainant. No physical evidence or CCTV footage exists."*

        **Family/Granted Example:**
        *"Filing for mutual consent divorce. Both parties have signed the settlement agreement covering property and child custody. No disputes remain."*
        """)

    case_description = st.text_area(
        "Describe your case",
        placeholder="Describe your case in detail: type of case, evidence available, witnesses, documentation, prior legal history, etc.",
        height=180,
        key="case_input"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        predict_btn = st.button("🔮 Predict Outcome", use_container_width=True)

    if predict_btn:
        if len(case_description.strip().split()) < 5:
            st.error("Please provide a more detailed description (at least 5 words).")
        else:
            with st.spinner("Analyzing your case..."):
                result = send_predict(case_description)

            if "error" in result:
                st.error(f"Prediction failed: {result['error']}")
                st.info("Make sure you've trained the model first: `python ml_model/train_model.py`")
            else:
                # Determine card class
                color = result.get("color", "gray")
                card_class = {"green": "pred-win", "red": "pred-lose"}.get(color, "pred-uncertain")
                bar_class = {"green": "conf-bar-fill-green", "red": "conf-bar-fill-red"}.get(color, "conf-bar-fill-orange")

                conf = result.get("confidence_score", 0)

                st.markdown(f"""
                <div class="pred-card {card_class}">
                    <h3>Predicted Outcome: {result.get('verdict', 'Unknown')}</h3>
                    <p style="color:#8b949e;">Outcome Label: <strong>{result.get('outcome', '').upper()}</strong></p>
                    <p><strong>Confidence Score: {conf}%</strong> — {result.get('confidence_label', '')}</p>
                    <div class="conf-bar-container">
                        <div class="{bar_class}" style="width:{conf}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # All probabilities
                st.markdown("### 📊 Probability Breakdown")
                probs = result.get("all_probabilities", {})
                sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)

                for label, prob in sorted_probs:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.progress(int(prob))
                    with col_b:
                        st.markdown(f"**{label.title()}** — {prob}%")

                st.markdown(f"""
                <div class="disclaimer">{result.get('disclaimer', '')}</div>
                """, unsafe_allow_html=True)


# ── 3. KNOWLEDGE BASE VIEWER ──
elif page == "📚 Knowledge Base":
    st.markdown("## 📚 Legal Knowledge Base")
    st.markdown("Browse all built-in legal information topics.")

    import json, os
    kbs_path = os.path.join(os.path.dirname(__file__), "../data/legal_kbs.json")
    with open(kbs_path) as f:
        kbs_data = json.load(f)

    # Filter by intent
    intents = list(set(e["intent"] for e in kbs_data))
    intent_labels = {
        "efiling": "📁 eFiling",
        "epay": "💳 ePay",
        "legal_aid": "⚖️ Legal Aid",
        "court_info": "🏛️ Court Info",
        "faq": "📖 Legal FAQs"
    }
    selected = st.selectbox("Filter by Topic", ["All"] + [intent_labels.get(i, i) for i in intents])

    st.markdown("---")

    for entry in kbs_data:
        label = intent_labels.get(entry["intent"], entry["intent"])
        if selected != "All" and label != selected:
            continue

        with st.expander(f"{label} — {entry['question']}"):
            st.markdown(entry["answer"])
            st.markdown(f'<span style="color:#484f58; font-size:0.75rem;">Keywords: {", ".join(entry["keywords"])}</span>', unsafe_allow_html=True)


# ── 4. ABOUT ──
elif page == "ℹ️ About":
    st.markdown("## ℹ️ About JurisMind")
    st.markdown("""
    **JurisMind** is an AI-powered legal assistance chatbot designed to automate Department of Justice (DOJ) service queries.

    ### 🏗️ Architecture
    | Component | Technology |
    |---|---|
    | Backend API | FastAPI (Python) |
    | Intent Classification | Groq API (LLaMA 3) |
    | Knowledge Base | JSON + RapidFuzz |
    | ML Model | scikit-learn (TF-IDF + Logistic Regression) |
    | Frontend | Streamlit |

    ### 🔑 Features
    - **eFiling assistance** — guide users through online case filing
    - **ePay support** — court fee payment information
    - **Legal Aid** — information on free legal services
    - **Court Info** — timings, case status, jurisdiction guidance
    - **Case Outcome Predictor** — ML model predicting win/lose probability

    ### 🚀 Running the Project
    ```bash
    # Terminal 1 — Start API
    uvicorn backend.main:app --reload --port 8000

    # Terminal 2 — Start Frontend
    streamlit run frontend/app.py
    ```

    ### ⚠️ Disclaimer
    JurisMind provides general legal information only. It does NOT constitute legal advice.
    Always consult a qualified advocate for specific legal matters.
    """)
