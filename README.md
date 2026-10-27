# ⚖️ JurisMind — Legal Assistance Chatbot

AI-powered chatbot for Department of Justice service queries.
Built with FastAPI, Streamlit, Groq API, and scikit-learn.

\---

## Project Structure

```
jurismind/
├── backend/
│   └── main.py              ← FastAPI server (all endpoints)
├── kbs/
│   └── kbs\\\_engine.py        ← Knowledge Base System (fuzzy search)
├── nlp/
│   └── nlp\\\_handler.py       ← Groq API for intent + responses
├── ml\\\_model/
│   ├── train\\\_model.py       ← Train the ML model (run once)
│   └── predictor.py         ← Case outcome prediction logic
├── frontend/
│   └── app.py               ← Streamlit UI
├── data/
│   ├── legal\\\_kbs.json       ← 15 legal Q\\\&A entries (KBS database)
│   └── case\\\_dataset.csv     ← ML training data
├── .env                     ← API keys (DO NOT commit to GitHub)
├── requirements.txt
├── setup.bat                ← Windows one-click setup
└── README.md
```

\---

## Step-by-Step Setup (Windows PC)

### Step 1 — Install Python

Download Python 3.11+ from https://python.org
During install: Check "Add Python to PATH"

### Step 2 — Get Groq API Key (FREE)

1. Go to https://console.groq.com
2. Sign up (free)
3. Go to API Keys → Create API Key
4. Copy the key

### Step 3 — Setup Project

```cmd
# Open folder in terminal (Shift+Right Click → Open Terminal)
cd jurismind

# Run setup script (creates venv, installs packages, trains model)
setup.bat
```

Or manually:

```cmd
python -m venv venv
venv\\\\Scripts\\\\activate
pip install -r requirements.txt
python ml\\\_model/train\\\_model.py
```

### Step 4 — Add API Key

Open `.env` file and replace:

```
GROQ\\\_API\\\_KEY=your\\\_groq\\\_api\\\_key\\\_here
```

With your actual key:

```
GROQ\\\_API\\\_KEY=gsk\\\_xxxxxxxxxxxxxxxxxxxx
```

### Step 5 — Run the Project

**Terminal 1 (Backend API):**

```cmd
venv\\\\Scripts\\\\activate
uvicorn backend.main:app --reload --port 8000
```

You should see: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 (Frontend):**

```cmd
venv\\\\Scripts\\\\activate
streamlit run frontend/app.py
```

Browser opens at: `http://localhost:8501`

\---

## API Endpoints

|Method|Endpoint|Description|
|-|-|-|
|GET|/|API status|
|POST|/chat|Main chat endpoint|
|POST|/predict|ML case prediction|
|POST|/search-kbs|Direct KBS search|
|GET|/health|Health check|
|GET|/docs|Swagger UI (auto-generated)|

Test API at: http://localhost:8000/docs

\---

## Tech Stack

|Component|Library|Purpose|
|-|-|-|
|Backend|FastAPI + Uvicorn|REST API server|
|NLP|Groq API (LLaMA 3)|Intent classification + responses|
|KBS|RapidFuzz|Fuzzy keyword matching|
|ML|scikit-learn|Case outcome prediction|
|Frontend|Streamlit|Chat UI|
|Config|python-dotenv|Environment variables|

\---

## Hardware Notes (Your PC)

* RX 7700 XT → ROCm only works on Linux, NOT needed for this project
* All ML training uses CPU (scikit-learn) → Works perfectly on your PC
* Groq API handles LLM inference on their servers → No GPU needed
* Total RAM needed: \~500MB

\---

## Add More KBS Entries

Edit `data/legal\\\_kbs.json` and add entries in this format:

```json
{
  "id": 16,
  "intent": "faq",
  "keywords": \\\["your", "keywords", "here"],
  "question": "Your question here?",
  "answer": "Your detailed answer here."
}
```

## Improve ML Model

Add more rows to `data/case\\\_dataset.csv` then retrain:

```cmd
python ml\\\_model/train\\\_model.py
```

\---

## Disclaimer
JurisMind provides general legal information only.
It does NOT constitute legal advice. Always consult a qualified lawyer.