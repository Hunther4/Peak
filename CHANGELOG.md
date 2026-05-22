# Changelog

## v1.0.0 (2026-05-22)

### 🚀 Initial Release — Fase 1 completa

Peak Practice, un sistema agéntico de práctica deliberada basado en los principios de Anders Ericsson.

#### Backend
- FastAPI + SQLModel con SQLite (WAL mode)
- Autenticación vía API Key con bcrypt + constant-time verify
- Ruteador dinámico de IA: Groq → OpenRouter → LM Studio local
- RAG con ChromaDB + embeddings HuggingFace (BAAI/bge-small-en-v1.5)
- Rate limiting con slowapi
- Security headers middleware (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- 279 tests, 76% coverage

#### Frontend
- React 19 + Vite + Zustand + TailwindCSS
- StatusIndicator en vivo (Server + AI semáforos)
- Skills, Timeline, SessionForm, Mental Reps, Challenges, RAG Books
- Modal accesible con focus trap y Escape key
- Pantalla de bienvenida con nombre + edad

#### Infraestructura
- systemd-run para servicios persistentes (peak-backend, peak-frontend)
- Launcher unificado (`peak_launcher.sh`)
- README bilingüe EN/ES
- Licencia GPLv3
