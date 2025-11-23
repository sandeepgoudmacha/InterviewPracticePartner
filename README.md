# Interview Practice Partner

An **AI-powered mock interview platform** that helps candidates prepare for job interviews with role-specific, multi-round interviews. Supports SDE (Technical → Coding → HR rounds), Data Scientist, Sales Representative (Hiring Manager → Senior Leadership rounds), and more with intelligent, personalized questions across technical, behavioral, coding, and sales domains.

## 📋 Quick Navigation

- [Quick Start](#quick-start)
- [Setup & Installation](#setup--installation)
- [Architecture](#architecture)
- [Design Decisions](#design-decisions)

---

## ⚡ Quick Start

### Few-Minutes Setup

```bash
# 1. Clone repository
git clone https://github.com/sandeepgoudmacha/InterviewPracticePartner.git
cd InterviewPracticePartner

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Create .env file
echo "MONGO_URL=your_mongo_url" > .env
echo "DEFAULT_GROQ_API_KEY=your_groq_key" >> .env

# 4. Frontend setup (new terminal)
cd frontend
npm install

# 5. Run both (in separate terminals)
# Terminal 1: cd backend && uvicorn app:app --reload --port 5000
# Terminal 2: cd frontend && npm run dev
```

Access at `http://localhost:5173`

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (async Python) |
| LLM | LangChain + Groq API (LLaMA 3.3 70B) |
| Database | MongoDB + PyMongo |
| Speech-to-Text | OpenAI Whisper |
| Confidence Scoring | librosa |
| NLP | Sentence Transformers |
| Authentication | JWT + Argon2 |
| Document Processing | PyMuPDF |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18+ with TypeScript |
| Build Tool | Vite |
| UI Components | Chakra UI |
| Vision | Face-api.js + TensorFlow.js |
| Code Editor | Monaco Editor |
| HTTP | Axios + Fetch API |
| Styling | Tailwind CSS + Emotion |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│          Frontend (React + TypeScript + Vite)           │
│  - Audio recording & playback                           │
│  - Face detection (attention tracking)                  │
│  - Code editor (Monaco)                                 │
│  - Feedback dashboard                                   │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (HTTP/HTTPS)
                     │
┌────────────────────▼────────────────────────────────────┐
│           Backend (FastAPI + LangChain)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  API Layer - Interview, Coding, Feedback         │   │
│  ├──────────────────────────────────────────────────┤   │
│  │  Session Management - User state & history       │   │
│  ├──────────────────────────────────────────────────┤   │
│  │  Services - Interview, Coding, HR, Sales, etc.   │   │
│  ├──────────────────────────────────────────────────┤   │
│  │  Utilities - Audio, Detection, Constraints       │   │
│  ├──────────────────────────────────────────────────┤   │
│  │  LangChain Chains - Question generation          │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼────┐  ┌───▼────┐
   │ MongoDB  │  │ Groq   │  │Whisper │
   │ Storage  │  │ API    │  │Speech  │
   └──────────┘  └────────┘  └────────┘
```

### Backend Services

**Interview Session Management**:
- **InterviewSession**: Technical Q&A with memory-based context
  - SDE: Algorithm & system design questions
  - Data Scientist: ML & statistics questions
  - Frontend/Backend: Role-specific technical questions
- **CodingSession**: Live coding with 2-3 problem rounds
  - Adaptive difficulty based on role
  - Real-time code evaluation
  - Constraint enforcement (no hints)
- **HRSession**: Behavioral interview (shared across all roles)
  - Communication assessment
  - Team collaboration evaluation
  - Growth mindset exploration
- **SalesSession**: Sales-specific two-round format
  - Round 1 (Hiring Manager): 2 questions on sales process
  - Round 2 (Senior Leadership): 2 questions on leadership fit

### Interview Agent Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Starts Interview                    │
│                   (Role + Round Selected)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  1. Determine Session Type         │
        │  (Technical/Coding/HR/Sales)       │
        └────────────┬───────────────────────┘
                     │
         ┌───────────┴───────────┬────────────────┬──────────────┐
         │                       │                │              │
         ▼                       ▼                ▼              ▼
    ┌─────────┐          ┌─────────────┐   ┌──────────┐   ┌──────────┐
    │Technical│          │   Coding    │   │   HR     │   │  Sales   │
    │Session  │          │  Session    │   │ Session  │   │ Session  │
    └────┬────┘          └──────┬──────┘   └────┬─────┘   └────┬─────┘
         │                      │               │              │
         ▼                      ▼               ▼              ▼
    ┌──────────────────────────────────────────────────────────────┐
    │  2. Load Context                                             │
    │  - User resume (if provided)                                 │
    │  - Previous responses (session memory)                       │
    │  - Role-specific guidelines                                  │
    └─────────────────┬────────────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────────────┐
         │  3. Generate Question (LLM Agent)  │
         │  - LangChain chain with memory     │
         │  - Groq API (LLaMA 3.3 70B)       │
         │  - Role-specific prompts           │
         └─────────────┬──────────────────────┘
                       │
                       ▼
         ┌────────────────────────────────────┐
         │  4. Ask User & Receive Audio       │
         │  - Real-time recording             │
         │  - Face detection (attention)      │
         │  - Record session for replay       │
         └─────────────┬──────────────────────┘
                       │
                       ▼
         ┌────────────────────────────────────┐
         │  5. Process User Response          │
         │  - Transcribe (Whisper)            │
         │  - Confidence scoring (librosa)    │
         │  - Off-topic detection             │
         │  - Confusion detection             │
         └─────────────┬──────────────────────┘
                       │
           ┌───────────┴──────────┐
           │                      │
           ▼                      ▼
    ┌─────────────┐        ┌──────────────┐
    │ Coding?     │        │ Off-topic or │
    │ (Constraint │        │ Confused?    │
    │ Check)      │        └──────┬───────┘
    └────┬────────┘               │
         │ YES                     │ YES
         ▼                         ▼
    ┌─────────────────┐    ┌─────────────────┐
    │ Enforce Coding  │    │ Provide Support │
    │ Constraints:    │    │ - Clarification │
    │ - No hints      │    │ - Guidance      │
    │ - No solutions  │    └─────────────────┘
    │ - Only guidance │               │
    └────┬────────────┘               │
         │ VIOLATION?                  │
         ▼                             │
    ┌──────────────┐                  │
    │ Ask Guiding  │                  │
    │ Questions    │                  │
    └────┬─────────┘                  │
         │                            │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────────────┐
         │  6. Store in Vector Memory         │
         │  - Semantic embeddings             │
         │  - Query history                   │
         └─────────────┬──────────────────────┘
                       │
                       ▼
         ┌────────────────────────────────────┐
         │  7. Check Round Progress           │
         │  - Questions remaining?            │
         │  - Continue or next round?         │
         └─────────────┬──────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼ More Questions             ▼ Round Complete
    Go to Step 3              ┌──────────────────────┐
         (Loop)               │  8. Generate Feedback│
                              │  - Score assessment  │
                              │  - Strengths         │
                              │  - Improvements      │
                              └──────────┬───────────┘
                                         │
                                         ▼
                            ┌────────────────────────┐
                            │   Interview Complete   │
                            │   User Receives Report │
                            └────────────────────────┘
```

---

## 🚀 Setup & Installation

### Prerequisites

```bash
# Check versions
python --version    # Should be 3.10 or higher
node --version      # Should be 18 or higher
```

- **MongoDB**: Cloud (Atlas) or local instance
- **Groq API Key**: Free tier at https://groq.com
- **Git**: For cloning repository

### Step 1: Clone Repository

```bash
git clone https://github.com/sandeepgoudmacha/InterviewPracticePartner.git
cd InterviewPracticePartner
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (choose based on OS)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
cd ../frontend
npm install
```

### Step 4: Environment Configuration

Create `backend/.env`:

```env
# MongoDB Configuration
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=interview_partner_db

# Groq API Configuration
DEFAULT_GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT Configuration
SECRET_KEY=your_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server Configuration
PORT=5000
HOST=0.0.0.0
```

Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_NAME=Interview Practice Partner
```

### Step 5: Get API Keys

**Groq API Key** (Free): Go to https://groq.com
**MongoDB** (Free): Go to https://www.mongodb.com/cloud/atlas

### Step 6: Run the Application

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app:app --reload --port 5000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

Access at `http://localhost:5173`

---

## 🎨 Design Decisions

### 1. Service-Oriented Architecture
**Why**: Each interview type has unique logic
- Easy to test independently
- Simple to add new interview types
- Clear separation of concerns

### 2. LangChain Memory-Based Q&A
**Why**: Context-aware questions based on resume
- Conversational history tracking
- Intelligent follow-ups
- Reduced API calls with caching

### 3. JSON Sanitization Layer
**Why**: Prevent NaN/Infinity errors
- All responses wrapped in `_response()`
- Handles edge cases in scoring
- Ensures consistent format

### 4. Multi-Layer Coding Constraints
**Why**: Prevent solution hints in coding
- Strict system prompt
- Response sanitization
- Fallback Guiding questions

### 5. Attention Tracking with Smoothing
**Why**: Reduce false "distracted" alerts
- Consistency counter (2 detections needed)
- Face in 10-90% of frame
- 3 consecutive non-detections to mark distracted

### 6. Vector Memory for Context
**Why**: Efficient off-topic detection
- Semantic similarity search
- Scalable to many responses
- Fast detection

---

## 🚀 Future Improvements

- [ ] **Deploy to production**
- [ ] Real-time transcription (WebSocket)
- [ ] Advanced analytics dashboard
- [ ] LinkedIn & job portal integration
- [ ] Resume AI review


