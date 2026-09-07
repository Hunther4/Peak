# Análisis Integral — Peak Practice

> Generado: 2026-05-24
> Propósito: Mapa completo del proyecto: lo que tenemos, lo que falta, lo que podríamos implementar.

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Stack Tecnológico](#2-stack-tecnológico)
3. [Arquitectura Actual](#3-arquitectura-actual)
4. [Lo que Tenemos (Bien)](#4-lo-que-tenemos-bien)
5. [Lo que Está Mal o Falta](#5-lo-que-está-mal-o-falta)
6. [Skills (Habilidades) Implementadas](#6-skills-habilidades-implementadas)
7. [Features Existentes — Mapa Detallado](#7-features-existentes--mapa-detallado)
8. [Features Planificadas pero NO Implementadas](#8-features-planificadas-pero-no-implementadas)
9. [Features Potenciales para el Futuro](#9-features-potenciales-para-el-futuro)
10. [Deuda Técnica y Bugs Conocidos](#10-deuda-técnica-y-bugs-conocidos)
11. [Seguridad](#11-seguridad)
12. [Testing](#12-testing)
13. [Métricas del Proyecto](#13-métricas-del-proyecto)
14. [Roadmap Recomendado](#14-roadmap-recomendado)
15. [Decisiones de Arquitectura Clave](#15-decisiones-de-arquitectura-clave)

---

## 1. Resumen Ejecutivo

Peak Practice es un **sistema agéntico de práctica deliberada** full-stack (FastAPI + React).
Genera auditorías de sesiones vía IA, mantiene un escalera adaptativa para memorización y matemáticas,
e indexa PDFs del usuario con RAG para que el coach tenga contexto personalizado durante las evaluaciones.

### Estado General: **B+** (sólido, con áreas críticas que mejorar)

| Dimensión | Nota | Por qué |
|-----------|------|---------|
| Backend | A- | Bien testeado, modular, buena arquitectura. Faltan índices, background tasks |
| Frontend | B | UI sólida, store Zustand limpio. Sin tests, polling en vez de WebSockets |
| Testing | B+ | Backend 32 archivos de test ~279 tests. Frontend: CERO tests |
| Seguridad | B | API Key con bcrypt, rate limiting, security headers. Uploads públicos, alguna inconsistencia |
| Deployment | D | Sin Docker, sin CI/CD, SQLite en producción, sin docker-compose |
| Skills | B- | 3 skills: 2 completas (Memory Number, Math Thinking), 1 placeholder (IQ Practice) |
| UX/UI | A- | Bien cuidada. Faltan estados de loading/error/vacío en algunas secciones |

---

## 2. Stack Tecnológico

### Backend
| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Framework | FastAPI | — |
| ORM | SQLModel (SQLAlchemy) | — |
| DB | SQLite + WAL mode | — |
| Auth | bcrypt + X-API-Key (middleware ASGI) | — |
| AI Router | Router interno (Groq / OpenRouter / LM Studio) | — |
| RAG | ChromaDB + BAAI/bge-small-en-v1.5 | — |
| Rate Limiting | slowapi | — |
| Rate Limiting Algo | Fixed Window + IP + API Key | — |

### Frontend
| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Framework | React | 19.2.6 |
| Build | Vite | 8.0.12 |
| State | Zustand | 5.0.13 |
| CSS | TailwindCSS | 4.3.0 |
| Lint | ESLint | 10.3.0 |

### Infraestructura
| Componente | Estado |
|------------|--------|
| Servicios | systemd --user (peak-backend, peak-frontend) |
| Launcher | peak_launcher.sh (bash) |
| CI/CD | ❌ No existe |
| Docker | ❌ No existe |
| Backup DB | ❌ No existe |

---

## 3. Arquitectura Actual

```
┌─────────────┐     HTTP/JSON      ┌──────────────────┐
│  Frontend   │ ◄─────────────────► │    Backend        │
│  React      │    X-API-Key Auth   │    FastAPI         │
│  Vite 5173  │                     │    Uvicorn 8000    │
│  Zustand    │                     │                    │
└─────────────┘                     └──────┬───────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
              ┌─────▼──────┐       ┌──────▼───────┐      ┌──────▼──────┐
              │ AI Router   │       │  SQLite DB   │      │  ChromaDB   │
              │ Groq        │       │  (peak.db)   │      │  (RAG)      │
              │ OpenRouter  │       │  WAL mode    │      │  PDFs       │
              │ LM Studio   │       └──────────────┘      └─────────────┘
              └────────────┘
```

### Backend: 14 routers (rutas API)
```
/api/skills, /api/sessions, /api/assessments, /api/dashboard,
/api/books (RAG), /api/mental, /api/models, /api/health,
/api/profile, /api/memory-game, /api/math-thinking, /api/cognitive
```

### Backend: 15 módulos core
```
core/ai.py          — Interfaz con modelos de IA
core/auth.py        — LazyAPIKeyManager + middleware
core/database.py    — SQLite engine + WAL+journal pragmas
core/limiter.py     — Rate limiting (slowapi + IP+Key)
core/memory_number.py — Engine de escalera adaptativa
core/math_thinking.py — Engine de problemas matemáticos
core/mental.py      — Mental reps + challenges engine
core/model_registry.py — Registro y scoring de modelos
core/rag.py         — ChromaDB + embeddings + search
core/router.py      — AI Router (selecciona modelo dinámico)
core/settings.py    — KV store en DB (AppSetting)
core/tasks.py       — Background tasks executor
core/utils.py       — Utilidades varias
core/auditor.py     — Auditor AI de sesiones
```

### Frontend: 17 componentes
```
App.jsx, WelcomeScreen.jsx, SkillCard.jsx, SessionForm.jsx,
Timeline.jsx, MemoryGame.jsx, MathThinkingGame.jsx,
DualNBackGame.jsx [SKELETON], BooksPanel.jsx, ModelInfo.jsx,
AiModeToggle.jsx, ProfileAvatar.jsx, MentalRepTimeline.jsx,
ChallengeList.jsx, StatusIndicator.jsx, AmbientParticles.jsx,
Spotlight.jsx, ui.jsx (ToastProvider)
```

---

## 4. Lo que Tenemos (Bien) ✅

### Arquitectura
- **Separación de concerns clara**: routers → services → core engines
- **AI Router multi-provider**: Groq, OpenRouter, LM Studio con selección dinámica y scoring
- **Rate limiting por IP + API Key**: protección contra abuso
- **Security headers**: X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- **WAL mode + busy_timeout**: SQLite configurado para concurrencia
- **Middleware auth**: ASGI middleware con bcrypt + constant-time comparison

### Frontend
- **UI cuidada** con glassmorphism, spotlight, particles, animaciones
- **Zustand store** limpio y modular (~427 líneas bien organizadas)
- **Componentes separados** con responsabilidad única
- **Error banner** global con dismiss
- **Profile guard** (WelcomeScreen hasta que el usuario se registre)

### Testing
- **32 archivos de test** en backend
- **~279 tests** (última medición)
- **Cobertura 76%** según README
- Tests de seguridad, modelos, rutas, engine, auditor, etc.

### Skills Implementadas
- **Pensamiento Matemático**: 10 niveles, AI-generated problems, escalera adaptativa, feedback paso a paso
- **Memorizar Números**: 7 fases, escalera adaptativa (span 4→80), digit_max progresivo

---

## 5. Lo que Está Mal o Falta ❌

### CRÍTICO
| Problema | Impacto | Dónde |
|----------|---------|-------|
| **No hay tests en frontend** | React components y Zustand store NO tienen ni un solo test | `frontend/` |
| **/uploads público sin auth** | Avatares y archivos subidos son accesibles por cualquiera | `backend/main.py:55` |

### HIGH
| Problema | Impacto | Dónde |
|----------|---------|-------|
| **Sin Docker** | No se puede reproducir el entorno fácilmente, deployment es manual | — |
| **Sin CI/CD** | Tests no corren automáticamente, no hay calidad garantizada en pushes | — |
| **SQLite en "producción"** | Para compartir con alguien más, SQLite no escala ni persiste en cloud | `backend/core/database.py` |
| **Dual N-Back es SKELETON** | `DualNBackGame.jsx` tiene 30 líneas, no genera estímulos, no envía trials | `frontend/src/components/DualNBackGame.jsx` |
| **IQ Practice es PLACEHOLDER** | `iq-practice.yaml` tiene literalmente 5 líneas | `backend/skills/iq-practice.yaml` |
| **Polling en vez de WebSockets** | `setTimeout` y `setInterval` para detectar fin de procesos async | `frontend/src/store/store.js` |

### MEDIUM
| Problema | Impacto | Dónde |
|----------|---------|-------|
| **Manejo de errores inconsistente** | console.warn vs throw según la acción | `frontend/src/store/store.js` |
| **Blocking RAG indexing** | index_books corre sincrónico, puede timeout en APIs grandes | `backend/core/rag.py` |
| **Sin migraciones de DB** | Los modelos se crean con `create_all`, no hay versioning | `backend/core/database.py` |
| **Hardcoded "local-model"** | Nombre del modelo LM Studio hardcodeado en vez de config | `backend/core/ai.py` |
| **No hay backup de la DB** | Si se corrompe peak.db, se pierde todo | — |
| **Faltan estados vacíos** | Algunas secciones (Books, Challenges) no muestran "no hay datos" | Varios componentes |
| **Bcrypt usa hashpw manual** | Usa `compare_digest` sobre hash en vez de `checkpw()` | `backend/core/auth.py` |

### LOW
| Problema | Impacto | Dónde |
|----------|---------|-------|
| **Faltan índices en DB** | Algunas queries no tienen index (created_at, skill_id ya están) | `backend/models/models.py` |
| **Sin environment validation** | Si falta GROQ_API_KEY, el error es opaco | — |
| **Linear metadata search** | `_load_metadata` lee JSON completo cada vez | `backend/core/rag.py` |
| **Sin lint check en CI** | ESLint configurado pero no se corre automáticamente | — |
| **Avatar upload sin validación** | No valida tipo MIME, tamaño máximo | `backend/api/routes/profile.py` |

---

## 6. Skills (Habilidades) Implementadas

| Skill | Tipo | Estado | Frontend | Backend | Tests |
|-------|------|--------|----------|---------|-------|
| **Memorizar Números** | memory_number | ✅ Completa | MemoryGame.jsx | core/memory_number.py + routes/memory_game.py | 37 tests |
| **Pensamiento Matemático** | problem_set | ✅ Completa | MathThinkingGame.jsx | core/math_thinking.py + routes/math_thinking.py | 17 tests |
| **Práctica de IQ** | placeholder | 🔸 Placeholder | ❌ No existe | ❌ No existe | ❌ |
| **Dual N-Back** | cognitive | 🔸 Skeleton | DualNBackGame.jsx (30 líneas) | routes/cognitive.py + cognitive_service.py | 1 test file |

### Detalle de cada skill

#### Memorizar Números
- **YAML**: memory-number.yaml — 7 fases, span 4→80, digit_max 1→9, ai_assisted en fase 7
- **Engine**: `calculate_staircase()` adaptativo con `correct_streak` tracking
- **Game loop**: presenting → recalling → feedback → (siguiente round o consolidate)
- **API**: 6 endpoints (createSession, createRound, submitAttempt, consolidate, getState, getHistory)

#### Pensamiento Matemático
- **YAML**: math-thinking.yaml — 10 niveles con topics específicos
- **Engine**: `generate_problem()` vía AI (router.execute_with_router), `evaluate_attempt()`, `calculate_staircase()`
- **Game loop**: ready → answering → feedback → (siguiente round o consolidate)
- **API**: 6 endpoints (misma estructura que Memory Number)
- **Niveles**: desde "básico" (suma/resta) hasta "integrado" (multi-paso/modelado)

#### Dual N-Back (Cognitive Telemetry)
- **Modelos**: CognitiveSkill, CognitiveSession, CognitiveTrial
- **Service**: `calcular_escalera_psicometrica()` — sube N si precision >= 0.80, baja si < 0.70
- **API**: POST /skills/, POST /sessions/, POST /trials/ (bulk), POST /sessions/{id}/finalize/
- **Frontend**: esqueleto de 30 líneas con `performance.now()` y key listener, no implementa estímulos

#### Práctica de IQ
- **YAML**: literalmente 5 líneas con `skill_type: placeholder`
- **No hay**: engine, routes, frontend, tests

---

## 7. Features Existentes — Mapa Detallado

### Core
- ✅ Sesiones de práctica deliberada con auditoria AI
- ✅ Evaluación automática de cada sesión
- ✅ Timeline de progreso histórico
- ✅ Skill Cards con métricas (sesiones, última práctica)
- ✅ SessionForm con modo quick/full + timer
- ✅ Perfil de usuario con nombre, edad, avatar upload
- ✅ WelcomeScreen para onboarding
- ✅ Dashboard con summary inteligente

### AI
- ✅ Router dinámico: Groq / OpenRouter / LM Studio
- ✅ Model scoring automatic (benchmark)
- ✅ Model selector: manual o auto
- ✅ Provider toggle (local vs cloud)
- ✅ Structured AI output via Pydantic
- ✅ AI audit de sesiones con feedback específico
- ✅ Rate limiting por proveedor

### RAG (Books)
- ✅ Indexación de PDFs en ChromaDB
- ✅ Búsqueda semántica (BAAI/bge-small-en-v1.5)
- ✅ Status polling durante indexación
- ✅ Búsqueda por query con top_k configurable

### Mental Representations
- ✅ Generación de representaciones mentales vía AI
- ✅ Aceptación/edición de representaciones
- ✅ Timeline de representaciones
- ✅ Challenges generados por AI
- ✅ Progress tracking en challenges
- ✅ Triggers: assessment, insight, session_batch

### Visual/UX
- ✅ Glassmorphism (glass-panel, backdrop-filter)
- ✅ Ambient background con blur orbs animados
- ✅ Ambient particles (fondo dinámico)
- ✅ Spotlight effect en cards (mouse tracking)
- ✅ Stagger animations en listas
- ✅ Spinner loading states
- ✅ Error banner con dismiss
- ✅ Responsive grid layout
- ✅ Modo oscuro nativo (neutral-950 background)

---

## 8. Features Planificadas pero NO Implementadas

Estas son cosas que YA existen como placeholder, mención, o "ya se habló de hacerlas" pero NO están hechas:

| Feature | Evidencia | Prioridad |
|---------|-----------|-----------|
| **Dual N-Back game logic** | Componente skeleton creado, backend listo, falta el juego | 🔴 ALTA |
| **IQ Practice skill** | YAML placeholder de 5 líneas, nada más | 🔴 ALTA |
| **Ngrok / deployment gratis** | Se analizó pero no se configuró | 🟠 MEDIA |
| **PostgreSQL migration** | Se mencionó para deploy en Vercel+Render+Neon | 🟠 MEDIA |
| **Service worker / PWA** | `frontend/` tiene service worker? No. Se mencionó en pwa-plan.md | 🟡 BAJA |
| **Strict TDD mode** | SDD init detectó que no se activó | 🟢 INFO |

---

## 9. Features Potenciales para el Futuro

Estas NO están planificadas pero serían mejoras naturales:

### Corto Plazo (1-2 sesiones)
- **WebSockets** para estado en tiempo real (en vez de polling)
- **Logros / Badges** por rachas de práctica
- **Exportar datos** (CSV/JSON del timeline)
- **Notificaciones desktop** para recordatorios de práctica
- **Sonidos** feedback auditivo en juegos (MemoryGame, MathThinking)

### Mediano Plazo (3-5 sesiones)
- **Autenticación multi-usuario** (no solo API Key global)
- **Comparativa entre usuarios** (opcional, leaderboard)
- **Calendario de práctica** (heatmap estilo GitHub)
- **Gráficos de progreso** (Chart.js o similar en dashboard)
- **Personalización de skills** (crear skills custom)
- **Multi-idioma** (i18n, ya hay base bilingüe EN/ES)
- **Modo offline** (PWA con service worker + IndexedDB)

### Largo Plazo (6+ sesiones)
- **Mobile app** (React Native o wrapper)
- **Compartir skills/resultados** en redes
- **Plan de estudio semanal** generado por AI
- **API pública** para integraciones externas
- **Análisis de correlaciones** (fatiga vs rendimiento)
- **Importar/exportar skills** entre instancias Peak

---

## 10. Deuda Técnica y Bugs Conocidos

### Bugs Conocidos (del último audit)
- **AI Result Polling**: setTimeout(3s) frágil, se pierde si el backend tarda más
- **MemoryGame field names**: ya fixeamos 4 CRITICAL (correctPositions, all_correct, etc.)
- **UnboundLocalError en submit_attempt**: ya fixeado
- **best_span tracking incorrecto**: ya fixeado

### Deuda Técnica

| Item | Impacto | Esfuerzo |
|------|---------|----------|
| Frontend tests (Vitest + RTL) | 🔴 Crítico | 3-4 sesiones |
| Docker + docker-compose | 🟠 Alto | 1 sesión |
| CI/CD (GitHub Actions) | 🟠 Alto | 1 sesión |
| WebSockets reemplazar polling | 🟠 Alto | 2 sesiones |
| PostgreSQL migration | 🟠 Alto | 2 sesiones |
| Migraciones DB (Alembic) | 🟡 Medio | 1 sesión |
| Avatar MIME validation | 🟡 Medio | 30 min |
| Error handling estandarizado frontend | 🟡 Medio | 1 sesión |
| Empty states en todos los componentes | 🟢 Bajo | 1 sesión |
| LM Studio model name a config | 🟢 Bajo | 15 min |
| Bcrypt checkpw en vez de compare_digest | 🟢 Bajo | 10 min |
| Linear metadata load a cache | 🟢 Bajo | 30 min |
| Environment validation startup | 🟢 Bajo | 30 min |

---

## 11. Seguridad

### Lo que está bien
- ✅ API Key con bcrypt (salt + hash)
- ✅ Constant-time comparison con hmac.compare_digest
- ✅ Rate limiting por IP + API Key
- ✅ CORS configurado (origen único)
- ✅ Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- ✅ API Key en memoria (no localStorage)
- ✅ Auth middleware en todas las rutas (excepto health y uploads)

### Lo que está mal
- ❌ **/uploads público** — Sin auth, cualquiera puede ver avatares
- ❌ **API Key loggeada en startup** — Se imprime en consola si se genera nueva
- ❌ **No hay validación de MIME en upload de avatar**
- ❌ **Sin limit por usuario** (es single-key, no multi-user)
- ❌ **SQLite sin cifrado** — Si alguien accede al server, tiene la DB completa
- ❌ **Sin HTTPS** — Solo HTTP localhost, pero en Ngrok/Render habría que agregarlo

---

## 12. Testing

### Backend (32 test files)
```
test_ai.py, test_ai_json_cleaning.py, test_assessments.py,
test_auditor.py, test_auth.py, test_cognitive.py,
test_dashboard.py, test_health_routes.py, test_input_security.py,
test_math_thinking.py, test_memory_number.py, test_mental.py,
test_mental_routes.py, test_model_registry.py, test_models.py,
test_models_routes.py, test_rag.py, test_router.py,
test_secrets.py, test_security.py, test_security_headers.py,
test_sessions.py, test_settings.py, test_skills_routes.py,
test_skills.py, test_tasks.py, test_timezone.py, test_utils.py,
test_z_security_tasks.py
```

### Frontend (0 test files)
- No hay Vitest configurado
- No hay React Testing Library
- No hay tests de componentes
- No hay tests del store Zustand

### Cobertura
- Backend: ~76% según README
- Frontend: 0%
- Global: ~40% estimado

### Lo que falta testear en backend
- Cognitive routes más coverage
- Profile routes
- Error paths en todos los routers (400, 404, 422, 500)
- Rate limiter edge cases
- RAG con datos reales (ChromaDB mocking es frágil)

---

## 13. Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos backend (.py) | 40+ |
| Archivos frontend (.jsx/.js) | 20+ |
| Tests backend | 32 archivos, ~279 tests |
| Tests frontend | 0 |
| Skills implementadas | 3 (2 completas, 1 placeholder) |
| Skills potenciales | Dual N-Back (skeleton), IQ (placeholder) |
| Componentes React | 17 |
| Rutas API | 14 routers, ~50+ endpoints |
| Modelos DB | ~12 tablas SQLModel |
| Líneas backend estimadas | ~5000+ |
| Líneas frontend estimadas | ~3000+ |
| Último commit | 97a9532 |
| Frecuencia de commits | Alta (muchas sesiones) |

---

## 14. Roadmap Recomendado

### 🔴 Sesión 1: Dual N-Back + IQ Practice
1. Implementar lógica Dual N-Back (visual + auditory streams)
2. Conectar con cognitive routes existentes
3. Implementar IQ Practice skill (al menos un MVP básico)

### 🔴 Sesión 2: Deuda crítica
1. Docker + docker-compose (backend + frontend + chroma)
2. GitHub Actions (test + lint en cada push)
3. /uploads auth protection

### 🟠 Sesión 3: Deployment
1. Migrar SQLite → PostgreSQL (Neon.tech)
2. Configurar Ngrok o Vercel+Render
3. HTTPS + variables de entorno

### 🟠 Sesión 4: Frontend testing
1. Configurar Vitest + React Testing Library
2. Tests para componentes críticos (SessionForm, MemoryGame, MathThinkingGame)
3. Tests para Zustand store (acciones asíncronas)

### 🟡 Sesión 5: Madurez
1. WebSockets para estado en tiempo real
2. Alembic migrations
3. Manejo de errores estandarizado
4. Empty states + loading en todos los componentes

### 🟢 Sesión 6+: Features futuras
1. Logros / Badges
2. Gráficos de progreso
3. Calendario de práctica
4. PWA / offline
5. Comparativa multi-usuario

---

## 15. Decisiones de Arquitectura Clave

| Decisión | Por qué | Alternativa considerada |
|----------|---------|------------------------|
| **SQLite en vez de PostgreSQL** | Simple, 0 setup, archivo único. Ideal para single-user | PostgreSQL para multi-user |
| **WAL mode** | Concurrencia reads/writes sin bloqueo total | — |
| **Zustand en vez de Redux** | Liviano, sin boilerplate, suficiente para este alcance | Redux Toolkit / Jotai |
| **TailwindCSS v4** | Última versión, @tailwindcss/vite plugin nativo | CSS Modules / Styled Components |
| **X-API-Key en vez de JWT** | Simple, single-user, un solo secret | JWT multi-user |
| **Bcrypt en vez de argon2** | Suficiente para API Key, estándar | argon2 (más seguro) |
| **ChromaDB en vez de Pinecone** | Local, gratis, embeddings locales | Pinecone / Weaviate (cloud, caro) |
| **BAAI/bge-small-en-v1.5** | Chico, rápido, decente para RAG local | OpenAI embeddings (pago) |
| **Polling en vez de WebSockets** | Simple de implementar, 0 dependencies | WebSockets (más complejo) |
| **systemd --user en vez de PM2** | Nativo Linux, sin Node dependency | PM2 / Supervisor / screen |

---

## Bonus: Árbol de Decisión — ¿Por dónde arrancar?

```
¿Querés compartir con tu novia?
│
├─ Sí, ya → Ngrok (sesión 3 parcial, rápido)
│
├─ Sí, pero permanente → PostgreSQL + Vercel+Render (sesión 3 completa)
│
└─ No, primero terminar features → Dual N-Back (sesión 1)

¿Te molesta que no haya tests en frontend?
│
├─ Sí → Sesión 4 (frontend testing)
│
└─ No, después → Se pospone

¿Vas a deployar en cloud?
│
├─ Sí → Docker + CI/CD + PostgreSQL (sesión 2+3)
│
└─ No, solo local → Dual N-Back + IQ Practice (sesión 1)
```
