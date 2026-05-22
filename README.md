# Peak Practice 🚀

**Agentic deliberate practice system based on Anders Ericsson's principles.**

*Sistema agéntico e inteligente de práctica deliberada basado en los principios de Anders Ericsson.*

Peak Practice is a full-stack deliberate practice platform that indexes your scientific literature (PDFs) via RAG and uses a dynamic agentic router to evaluate sessions, calculate cognitive deviations, and generate progressively harder challenges — all without vendor lock-in. Bring your own LLM (Groq, OpenRouter, or local LM Studio) and your own books.

<!-- Screenshot: peak-dashboard.png -->

---

## Tech Stack

- **Frontend:** React, Vite, Zustand, TailwindCSS + PWA Ready
- **Backend:** FastAPI, SQLModel (SQLite with PRAGMA journal_mode=WAL for high concurrency)
- **AI Layer:** Dynamic agentic router (Groq / OpenRouter / LM Studio local) with strict Pydantic contracts for structured output
- **Vector DB (RAG):** ChromaDB + Local HuggingFace embeddings (BAAI/bge-small-en-v1.5)

<!-- Screenshot: architecture-diagram.png -->

---

## Quick Start

```bash
git clone https://github.com/Hunther4/Peak.git && cd Peak
chmod +x peak_launcher.sh
./peak_launcher.sh
```

The launcher starts both the backend (port 8000) and frontend (port 5173) automatically.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure as needed. The launcher reads `.env` automatically.

| Variable | Description | Required / Default |
|---|---|---|
| `PEAK_API_KEY` | Auth key for the backend API | Auto-generated if not set |
| `CORS_ORIGIN` | Frontend URL for CORS | `http://localhost:5173` |
| `DISABLE_AUTH` | Set to `1` to disable auth in dev | — |
| `GROQ_API_KEY` | Groq cloud inference key | Required for API mode |
| `OPENROUTER_API_KEY` | OpenRouter fallback key | Required for OpenRouter mode |
| `LM_STUDIO_BASE_URL` | Local AI server URL | `http://localhost:1234/v1` |
| `VITE_PEAK_API_KEY` | Frontend env, must match `PEAK_API_KEY` | Same as backend key |
| `VITE_API_URL` | Frontend env, backend API URL | `http://localhost:8000/api` |

---

## Architecture

```
User → Frontend (React) → API (FastAPI) → AI Router (Groq/OpenRouter/LM Studio) + RAG (ChromaDB) → Structured response → Feedback loop
```

The frontend sends practice sessions to the FastAPI backend, which delegates to the dynamic AI router. The router selects the best available model, augments the prompt with relevant context from your personal PDF library via ChromaDB RAG, and returns structured, validated output via Pydantic contracts. Results flow back through the API for storage, analysis, and dashboard visualization — closing the deliberate practice loop.

<!-- Screenshot: session-flow.png -->

---

## Testing

- 279 tests passing
- 76% code coverage
- TDD workflow (tests before code)

---

## License

```
GNU General Public License v3.0 (GPLv3)

Peak Practice — Agentic deliberate practice system.
Copyright (C) 2024-2026 Hunther4

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

---

## 🇪🇸 Español

# Peak Practice 🚀

**Sistema agéntico e inteligente de práctica deliberada basado en los principios de Anders Ericsson.**

*Agentic deliberate practice system based on Anders Ericsson's principles.*

Peak Practice es una plataforma full-stack de práctica deliberada que indexa tu literatura científica (PDFs) via RAG y utiliza un router agéntico dinámico para evaluar sesiones, calcular desviaciones cognitivas y generar desafíos progresivamente más difíciles — sin dependencia de un proveedor específico. Usa tu propio LLM (Groq, OpenRouter o LM Studio local) y tus propios libros.

<!-- Screenshot: peak-dashboard.png -->

---

### Stack Tecnológico

- **Frontend:** React, Vite, Zustand, TailwindCSS + PWA Ready
- **Backend:** FastAPI, SQLModel (SQLite con PRAGMA journal_mode=WAL para alta concurrencia)
- **Capa de IA:** Router agéntico dinámico (Groq / OpenRouter / LM Studio local) con contratos Pydantic estrictos para salida estructurada
- **BD Vectorial (RAG):** ChromaDB + Embeddings locales de HuggingFace (BAAI/bge-small-en-v1.5)

<!-- Screenshot: architecture-diagram.png -->

---

### Inicio Rápido

```bash
git clone https://github.com/Hunther4/Peak.git && cd Peak
chmod +x peak_launcher.sh
./peak_launcher.sh
```

El lanzador inicia tanto el backend (puerto 8000) como el frontend (puerto 5173) automáticamente.

---

### Variables de Entorno

Copia `backend/.env.example` a `backend/.env` y configura según sea necesario. El lanzador lee `.env` automáticamente.

| Variable | Descripción | Requerido / Default |
|---|---|---|
| `PEAK_API_KEY` | Clave de autenticación para la API del backend | Auto-generada si no se define |
| `CORS_ORIGIN` | URL del frontend para CORS | `http://localhost:5173` |
| `DISABLE_AUTH` | Configurar a `1` para deshabilitar auth en desarrollo | — |
| `GROQ_API_KEY` | Clave de inferencia cloud de Groq | Requerida para modo API |
| `OPENROUTER_API_KEY` | Clave de respaldo de OpenRouter | Requerida para modo OpenRouter |
| `LM_STUDIO_BASE_URL` | URL del servidor local de IA | `http://localhost:1234/v1` |
| `VITE_PEAK_API_KEY` | Variable del frontend, debe coincidir con `PEAK_API_KEY` | Misma clave del backend |
| `VITE_API_URL` | Variable del frontend, URL de la API del backend | `http://localhost:8000/api` |

---

### Arquitectura

```
Usuario → Frontend (React) → API (FastAPI) → Router IA (Groq/OpenRouter/LM Studio) + RAG (ChromaDB) → Respuesta estructurada → Bucle de retroalimentación
```

El frontend envía sesiones de práctica al backend FastAPI, que delega en el router dinámico de IA. El router selecciona el mejor modelo disponible, aumenta el prompt con contexto relevante de tu biblioteca personal de PDFs via ChromaDB RAG, y devuelve una respuesta estructurada y validada mediante contratos Pydantic. Los resultados vuelven a través de la API para almacenamiento, análisis y visualización en el dashboard — cerrando el ciclo de práctica deliberada.

<!-- Screenshot: session-flow.png -->

---

### Tests

- 279 pruebas pasando
- 76% de cobertura de código
- Flujo de trabajo TDD (tests antes del código)

---

### Licencia

```
GNU General Public License v3.0 (GPLv3)

Peak Practice — Sistema agéntico de práctica deliberada.
Copyright (C) 2024-2026 Hunther4

Este programa es software libre: puedes redistribuirlo y/o modificarlo
bajo los términos de la GNU General Public License publicada por
la Free Software Foundation, ya sea la versión 3 de la Licencia, o
(a tu elección) cualquier versión posterior.

Este programa se distribuye con la esperanza de que sea útil,
pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de
COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR.  Ver la
GNU General Public License para más detalles.

Deberías haber recibido una copia de la GNU General Public License
junto con este programa.  Si no es así, visita <https://www.gnu.org/licenses/>.
```
