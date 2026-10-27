from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kbs.kbs_engine import search_kbs
from nlp.nlp_handler import classify_intent, generate_groq_response
from ml_model.predictor import predict_case_outcome

app = FastAPI(
    title="JurisMind API",
    description="Legal Assistance Chatbot Backend — Department of Justice",
    version="1.0.0"
)

# Allow Streamlit frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request / Response Models ───────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    intent: str
    source: str          # "kbs", "groq", "ml", "greeting"
    kbs_match_score: Optional[float] = None

class PredictRequest(BaseModel):
    case_description: str

class KBSSearchRequest(BaseModel):
    query: str

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "JurisMind API is running. Visit /docs for API documentation."}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Main chat endpoint.
    Flow: Classify intent → Search KBS → If not found, use Groq LLM
    """
    user_msg = req.message.strip()

    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Step 1: Classify intent
    intent = classify_intent(user_msg)

    # Step 2: Handle greeting
    if intent == "greeting":
        return ChatResponse(
            reply="Hello! I'm JurisMind, your AI legal assistant. I can help you with eFiling, court fee payments, legal aid, case status, and general legal questions. How can I assist you today?",
            intent="greeting",
            source="greeting"
        )

    # Step 3: Handle ML prediction request
    if intent == "ml_predict":
        return ChatResponse(
            reply="Sure! To predict your case outcome, please use the **Case Outcome Predictor** tab on the left sidebar. Describe your case in detail there and our ML model will analyze it.",
            intent="ml_predict",
            source="system"
        )

    # Step 4: Search KBS
    kbs_result = search_kbs(user_msg)

    if kbs_result["found"]:
        return ChatResponse(
            reply=kbs_result["answer"],
            intent=kbs_result["intent"],
            source="kbs",
            kbs_match_score=kbs_result["score"]
        )

    # Step 5: Fallback to Groq LLM
    groq_reply = generate_groq_response(user_msg)
    return ChatResponse(
        reply=groq_reply,
        intent=intent,
        source="groq",
        kbs_match_score=kbs_result["score"]
    )

@app.post("/predict")
def predict(req: PredictRequest):
    """
    ML model endpoint for case outcome prediction.
    """
    if not req.case_description.strip():
        raise HTTPException(status_code=400, detail="Case description cannot be empty.")

    if len(req.case_description.split()) < 5:
        raise HTTPException(status_code=400, detail="Please provide a more detailed case description (at least 5 words).")

    try:
        result = predict_case_outcome(req.case_description)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/search-kbs")
def search(req: KBSSearchRequest):
    """Direct KBS search endpoint."""
    result = search_kbs(req.query)
    return result

@app.get("/health")
def health():
    return {"status": "healthy", "service": "JurisMind API"}
