# 🤖 AI Meeting Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-19.2.0-61DBFB.svg?logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

An intelligent, full-stack video conferencing application featuring real-time transcription, an AI-powered meeting co-pilot, and RAG-based document context retrieval. Transform standard video calls into smart, interactive workspaces.

---

## ✨ Key Features

- 📹 **Real-Time Video Conferencing**: Multi-participant high-quality audio & video using WebRTC and the Twilio SDK.
- 🎙️ **Live Transcription**: Sub-300ms speech-to-text using Deepgram, streamed over WebSockets to all participants.
- 🧠 **AI Meeting Co-Pilot**: Real-time context monitoring with Groq (Llama 3.1 70B) for automatic action item suggestions and meeting clarifications.
- 📚 **RAG Knowledge Base**: Upload meeting materials (PDF, DOCX) and perform intelligent Q&A over document contexts using a fast FAISS vector store.
- 🔒 **Secure Authentication & Storage**: Session management and persistent PostgreSQL data modeling powered by Supabase.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 19 + Vite + React Router
- **Styling**: Tailwind CSS
- **Integrations**: Twilio Video SDK, Supabase JS Client, Lucide React

### Backend
- **Framework**: FastAPI (Async) + Uvicorn
- **Database ORM**: SQLAlchemy (AsyncPG) mapped to Supabase PostgreSQL
- **AI & ML**: Deepgram SDK (Transcription), Groq SDK (LLM Gen), Sentence Transformers (Embeddings), FAISS (Vector DB)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Caching / WebSockets**: Redis
- **BaaS**: Supabase (Auth + PostgreSQL Database)

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Node.js** (v18+)
- **Python** (v3.9+)
- **Docker** desktop running (for Redis & local setups)

You will also need API keys from the following platforms:
- [Twilio](https://console.twilio.com/) (Video/WebRTC token generation)
- [Deepgram](https://console.deepgram.com/) (Real-time transcription)
- [Groq](https://console.groq.com/) (Fast LLM inference)
- [Supabase](https://supabase.com/) (PostgreSQL URL & Auth keys)

---

### Setup Instructions

#### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-meeting-assistant.git
cd ai-meeting-assistant
```

#### 2. Environment Variables Configuration

Create a `.env` file in the **`backend`** directory:
```env
TWILIO_ACCOUNT_SID=your_twilio_acc_sid
TWILIO_API_KEY_SID=your_twilio_api_key
TWILIO_API_KEY_SECRET=your_twilio_secret
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.supabase.co:5432/postgres
REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:5173
```

Create a `.env` file in the **`Frontend`** directory:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your_project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_TWILIO_API_KEY_SID=your_twilio_api_key
VITE_TWILIO_API_KEY_SECRET=your_twilio_secret
```

#### 3. Start the Backend

Start Redis via Docker:
```bash
cd backend
docker-compose up -d redis
```

Install Python dependencies and run the API:
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Start the Frontend

In a new terminal window:
```bash
cd Frontend
npm install
npm run dev
```

Your system is now fully running! Visit `http://localhost:5173` to sign in.

---

## 🎯 Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Meeting  │  │  Video   │  │   RAG    │  │   Auth   │   │
│  │Interface │  │ Component│  │ Component│  │  Pages   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        │ REST API    │ WebSocket   │ REST API    │ Supabase
        │             │             │             │ Auth
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Supabase │  │ Deepgram │  │   Groq   │  │  Twilio  │   │
│  │PostgreSQL│  │   STT    │  │   LLM    │  │  Video   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
