import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file!")

client = Groq(api_key=api_key)

INTENT_SYSTEM_PROMPT = """You are an intent classifier for a Department of Justice legal chatbot.
Classify the user's message into ONE of these intents:
- efiling       → questions about online case filing, eFiling portal, document upload
- epay          → questions about court fee payment, fee structure, online payment
- legal_aid     → questions about free legal help, NALSA, DLSA, lawyers for poor
- court_info    → questions about court timings, case status, jurisdiction, which court
- faq           → general legal questions: FIR, bail, divorce, consumer complaints, RTI
- ml_predict    → user wants to predict their case outcome or win probability
- greeting      → hello, hi, greetings, thanks
- unknown       → cannot classify

Respond with ONLY the intent label, nothing else. Example: "efiling"
"""

def classify_intent(user_message: str) -> str:
    """
    Uses Groq LLM to classify user intent.
    Returns intent string.
    """
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=20,
            temperature=0,
        )
        intent = response.choices[0].message.content.strip().lower()
        # Validate it's a known intent
        valid_intents = ["efiling", "epay", "legal_aid", "court_info", "faq", "ml_predict", "greeting", "unknown"]
        return intent if intent in valid_intents else "unknown"
    except Exception as e:
        print(f"[NLP ERROR] {e}")
        return "unknown"

def generate_groq_response(user_message: str, context: str = "") -> str:
    """
    Uses Groq to generate a conversational response when KBS has no match.
    context = KBS answer or additional info passed to ground the response.
    """
    system_prompt = """You are JurisMind, an AI legal assistant for the Department of Justice (India).
You help citizens with legal queries about courts, eFiling, ePay, legal aid, and general legal procedures.
Be concise, helpful, and always recommend consulting a professional lawyer for serious matters.
If you don't know something specific, say so and direct the user to official portals or helplines.
Never give advice that could replace a real lawyer. Keep responses under 150 words."""

    messages = [{"role": "system", "content": system_prompt}]

    if context:
        messages.append({
            "role": "system",
            "content": f"Relevant context from our knowledge base: {context}"
        })

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            max_tokens=200,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I'm having trouble connecting to the AI service. Error: {str(e)}. Please try again."