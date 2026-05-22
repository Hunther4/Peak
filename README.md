# Peak Practice App — Fase 1

> "Tu ciudadela privada de práctica deliberada"

---

## Stack

- **Backend:** FastAPI + SQLModel + SQLite
- **Frontend:** React + Vite + TailwindCSS + Zustand
- **IA (Fase 2):** LM Studio local

---

## Estructura

```
peak/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── seed.py              # Crear skills iniciales (correr 1 vez)
│   ├── requirements.txt
│   ├── core/
│   │   └── database.py      # SQLite config
│   ├── models/
│   │   └── models.py        # Skill, Session, Assessment, MentalRep, Challenge
│   ├── api/routes/
│   │   ├── skills.py
│   │   ├── sessions.py
│   │   ├── assessments.py
│   │   └── dashboard.py
│   └── skills/              # YAMLs de config por skill (Fase 2)
├── frontend/
│   ├── package.json
│   └── src/
│       ├── api/client.js    # Fetch wrapper
│       ├── store/store.js   # Zustand
│       ├── components/      # UI reutilizable
│       └── pages/           # Dashboard, Sessions, etc
└── README.md
```

---

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python seed.py        # Crea skills de Memoria y Matemáticas
uvicorn main:app --reload
# API disponible en http://localhost:8000
# Docs en http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
# App en http://localhost:5173
```

---

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /api/skills/ | Listar skills |
| POST | /api/skills/ | Crear skill |
| GET | /api/sessions/ | Listar sesiones |
| POST | /api/sessions/ | Crear sesión (Quick o Full) |
| GET | /api/assessments/ | Listar assessments |
| POST | /api/assessments/ | Crear assessment |
| GET | /api/dashboard/summary | Resumen por skill |
| GET | /api/dashboard/timeline | Timeline de actividad |

---

## Skills pre-configuradas

| Skill | Domain | Tipo |
|-------|--------|------|
| Memoria | memory | staircase (dígitos) |
| Matemáticas | math | problem_set |

---

## Fases

- ✅ **Fase 1:** CRUD + Dashboard (estás aquí)
- 🔲 **Fase 2:** LM Studio + AI Coach
- 🔲 **Fase 3:** RAG (libros → ChromaDB)
- 🔲 **Fase 4:** MentalRep versionado
- 🔲 **Fase 5:** Assessments + Leveling
