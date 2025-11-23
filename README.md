# Interview Practice Partner

An AI-powered interview preparation platform that helps candidates practice and improve their interview skills through realistic AI-driven interviews.

## 🌟 Features

- **Multiple Interview Types**
  - Technical/Coding interviews
  - HR behavioral interviews
  - Sales interviews
  - Memory-based challenges

- **AI-Powered Feedback**
  - Real-time response evaluation
  - Confidence scoring based on audio analysis
  - Comprehensive feedback reports
  - Performance analytics

- **Technical Capabilities**
  - Resume parsing and analysis
  - Speech recognition (Whisper)
  - Attention tracking
  - Vector-based Q&A memory

## 🏗️ Project Structure

The project follows a modern full-stack architecture:

```
📦 Interview Practice Partner
├── 📂 backend/                # FastAPI backend
│   ├── config/               # Configuration module
│   ├── services/             # Business logic
│   ├── routes/               # API endpoints
│   ├── models/               # Data models
│   ├── utils/                # Utility functions
│   └── chains/               # LangChain interview chains
│
└── 📂 frontend/              # React/TypeScript frontend
    └── src/
        ├── components/       # React components
        ├── pages/            # Page components
        ├── services/         # API services
        ├── constants/        # App constants
        ├── types/            # TypeScript types
        └── hooks/            # Custom React hooks
```

**📖 For detailed structure information, see [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)**

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB
- Groq API Key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Variables

Create `.env` in backend directory:
```
MONGO_URL=<your-mongodb-connection-string>
DB_NAME=interview_partner
DEFAULT_GROQ_API_KEY=<your-groq-api-key>
SECRET_KEY=<your-secret-key>
```

Create `.env.local` in frontend directory:
```
VITE_API_URL=http://localhost:8000
```

### Running Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Backend will be available at `http://localhost:8000`
Frontend will be available at `http://localhost:5173`

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **LLM**: Groq (Llama 3.3 70B)
- **Database**: MongoDB
- **AI/ML**: LangChain, HuggingFace Embeddings
- **Audio**: Whisper (OpenAI), librosa
- **Auth**: JWT + Argon2
- **Server**: Uvicorn

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Real-time**: Face detection (face-api.js)
- **State**: Component-based with hooks

## 📚 Documentation

- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Complete project structure guide
- [RESTRUCTURING_SUMMARY.md](./RESTRUCTURING_SUMMARY.md) - What changed in recent restructuring
- [QUICKREF.md](./QUICKREF.md) - Quick reference for developers

## 🔄 Recent Changes

The project was recently restructured for better maintainability:

### ✅ Completed
- Organized backend into logical modules (config, utils, services, routes, chains)
- Established frontend service layer and type system
- Created comprehensive documentation
- Enhanced `.gitignore`

### ⏳ In Progress
- Updating all imports in existing files
- Migrating session services
- Full test suite validation

See [RESTRUCTURING_SUMMARY.md](./RESTRUCTURING_SUMMARY.md) for details.

## 📝 API Endpoints

### Authentication
- `POST /signup` - Register new user
- `POST /login` - User login
- `GET /profile` - Get user profile

### Interviews
- `POST /interview/start` - Start new interview
- `POST /interview/submit-answer` - Submit interview response
- `GET /interview/{id}` - Get interview details
- `GET /interviews` - List user interviews

### Feedback
- `GET /feedback/{interview_id}` - Get interview feedback

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 🐳 Docker

Run with Docker Compose:

```bash
docker-compose up
```

## 📦 Deployment

### Heroku
The project includes a `Procfile` for Heroku deployment.

### Docker
Both backend and frontend have Dockerfile configurations.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## 📄 License

See LICENSE file for details

## 👥 Team

Built with ❤️ for interview preparation

## 🆘 Support

For issues and questions, please use the project's issue tracker.

---

**Status**: MVP Phase - Core features implemented and tested
**Last Updated**: November 2025
