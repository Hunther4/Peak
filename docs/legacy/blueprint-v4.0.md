# Blueprint v4.0 — Peak Practice App
### "Tu ciudadela privada de práctica deliberada"

---

## Filosofía (inamovible)

- Un solo usuario. Sin SaaS. Sin terceros innecesarios.
- LM Studio primero. Claude solo como oráculo de último recurso.
- La app es la mejor del mundo en exactamente 3 cosas:
  1. Versionar cómo evoluciona tu mente sobre una habilidad
  2. Rechazarte activamente cuando te mientes
  3. Conectar cada sesión con el conocimiento de tus libros

---

## Hardware & Entorno

| Componente | Detalle |
|-----------|---------|
| GPU | AMD RX 9060 XT 16GB VRAM (ROCm) |
| CPU | Ryzen 5 7600X |
| RAM | 32GB |
| OS | Linux Mint |
| IA Local | LM Studio (servidor en http://localhost:1234/v1) |
| Modelos recomendados | Llama 3.1 8B Q4 / Mistral 7B Q4 |

---

## Stack

| Capa | Tecnología | Razón |
|------|-----------|-------|
| Frontend | React + Vite + TailwindCSS | Rápido, conocido |
| Estado | Zustand | Simple, sin boilerplate |
| Backend | FastAPI + SQLModel | Ideal para IA, tipado |
| DB | **SQLite** | Un solo usuario. No necesitás PostgreSQL. Punto. |
| IA Principal | LM Studio (API compatible con OpenAI SDK) | Local, privado, sin costo |
| IA Oráculo | Claude API | Solo si LM Studio falla o confianza < 0.6 |
| RAG | LlamaIndex + ChromaDB | Pipeline maduro, todo local |
| Auth | **API Key simple** (local) o JWT (si querés aprender) | Para un solo usuario en local, API key alcanza |
| Cliente IA | openai Python SDK | Funciona directo con LM Studio sin cambios |
| Deploy | Local primero. Railway + Vercel después. | |

### Nota sobre la DB

SQLite es la opción correcta para un solo usuario. Rápido, backups son un archivo, no hay servicio que levantar. NO diseñes para una migración a PostgreSQL que probablemente nunca pase. Si el día de mañana necesitás Postgres, cruzás ese puente cuando llegue.

---

## Integración LM Studio

LM Studio expone un servidor OpenAI-compatible. La conexión es trivial:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # cualquier string, no se valida
)
```

Sin warmup especial — LM Studio mantiene el modelo cargado en VRAM. JSON forzado vía prompt + validación Pydantic.

---

## Modelo de Datos

```python
# Skill — La habilidad
Skill:
  id, name, domain        # "piano", "programación", "escritura"
  current_level           # 1-100
  created_at

# MentalRep — Git para tu cerebro
MentalRep:
  id, skill_id
  description             # "Antes veía X, ahora lo veo como Y"
  version                 # v1, v2, v3 — autoincremental
  trigger                 # qué evento de nivel lo provocó
  created_at

# Session — El Auditor
Session:
  id, skill_id
  duration_minutes
  what_i_practiced        # específico y concreto
  difficulty              # 1-5
  micro_error_found       # OBLIGATORIO en UI, siempre
  correction_applied      # OBLIGATORIO en modo Full, nullable en Quick
  hypothesis_tomorrow     # OBLIGATORIO en modo Full, nullable en Quick
  entry_mode              # "quick" | "full"
  ai_fields_status        # "pending" | "completed" (solo para quick)
  was_deliberate          # bool, calculado por IA
  ai_audit_log            # JSON: {score, verdict, reasoning, book_citations, domain_notes}
  onboarding_mode         # bool: primeras 14 sesiones, IA comenta sin rechazar
  created_at

# Challenge — Próximo reto generado por IA
Challenge:
  id, skill_id
  description             # concreto y medible
  difficulty_target       # 1-5
  source_book             # "Peak cap.3"
  source_chunk_id         # referencia al vector en ChromaDB
  completed               # bool
  created_at
```

---

## Quick Log — UX Post-Sesión (NUEVO en v4.0)

**Problema:** después de 45 minutos de práctica deliberada, estás cansado. 5 campos obligatorios con validación semántica es demasiada fricción. Si la app es un hábito, la fricción debe ser MÍNIMA.

### Dos modos de entrada

| | Quick (default) | Full |
|---|---|---|
| Campos que llenás | 3: qué, dificultad, error | 5: todos |
| correction_applied | IA lo genera en background | Lo ponés vos |
| hypothesis_tomorrow | IA lo genera en background | Lo ponés vos |
| Tiempo estimado | ~30 segundos | ~3 minutos |
| Auditoría | Se evalúa cuando IA completa los campos | Inmediata |

### Flujo Quick Log

1. User entra 3 campos → sesión guarda con `entry_mode=quick`, `ai_fields_status=pending`
2. Backend dispara LM Studio en background para generar `correction_applied` + `hypothesis_tomorrow`
3. Dashboard muestra badge "completando..." en la sesión por unos segundos
4. Cuando la IA termina → `ai_fields_status=completed` → se corre la auditoría normal
5. User puede entrar a la sesión y editar lo que la IA puso
6. Si LM Studio está apagado, los campos quedan `pending` sin bloquear — el user puede completarlos después

### Modo Full

Los 5 campos, exactamente como en el blueprint original. Para cuando tenés energía y querés control total.

### Auditoría diferida

La validación (onboarding/normal) opera sobre la sesión COMPLETA. No en el momento de entrada. Si la IA generó cualquier cosa, el Auditor la va a rechazar igual — pero el user ya se fue a dormir.

---

## Arquitectura de la IA

```
Session POST
    ↓
¿entry_mode = quick?
    ├─ Sí → guardar con ai_fields_status=pending → task en background
    │        └─ LM Studio genera correction_applied + hypothesis_tomorrow
    │              └─ ai_fields_status=completed → Auditor evalúa
    └─ No → validar campos obligatorios (full) → 400 si faltan
              ↓
         RAG: ChromaDB busca chunks relevantes de tus libros
              ↓
         LM Studio (OpenAI SDK) → JSON estructurado
              ↓ si confidence < 0.6 o falla
         Claude API (oráculo)
              ↓
         Pydantic valida JSON → reintenta 1 vez si inválido
              ↓
         Guarda Session en DB
              ↓
         Si was_deliberate = true → genera nuevo Challenge
```

---

## Sistema del Auditor

### Modo Onboarding (primeras 14 sesiones por habilidad)
- Los 3+ campos siguen siendo obligatorios según el modo
- IA no rechaza — solo comenta y puntúa
- Objetivo: entrenar granularidad de observación

### Modo Normal (sesión 15+)
- `was_deliberate = false` → sesión guardada, no suma a `current_level`
- UI muestra exactamente por qué fue rechazada + cita del libro fuente

### Criterios de rechazo (Peak / Ericsson)
1. `what_i_practiced` es vago o genérico (detectado por IA)
2. `micro_error_found` es "ninguno" o equivalente
3. `difficulty ≤ 2` por más de 3 sesiones consecutivas
4. `hypothesis_tomorrow` repite la sesión anterior
5. **Habilidades blandas:** IA usa criterios de especificidad conceptual, no técnica (ver Prompt del Coach)

---

## Versionado de Representación Mental

*Trigger automático para reescribir MentalRep:*
- `current_level` sube 10 puntos, O
- 20 sesiones sin actualizar la representación

*UI presenta la versión anterior y pregunta:*
> "¿Cómo ves esto ahora que no podrías haber articulado en v1?"

*La IA compara v_anterior vs v_nueva:*
- Similar → rechaza la actualización
- Distancia real → aprueba y registra trigger

---

## Prompt del Coach (núcleo del sistema)

```
SYSTEM:
Eres un auditor de práctica deliberada. Tu única función es evaluar
si una sesión cumple los criterios de Anders Ericsson en "Peak".

Libros de referencia disponibles (vía RAG):
- Peak — Anders Ericsson
- Atomic Habits — James Clear
- Outliers — Malcolm Gladwell
[+ los que el usuario agregue]

Criterios de evaluación:
1. ¿El objetivo fue específico y acotado?
2. ¿Estaba en el borde del límite actual (difficulty ≥ 3)?
3. ¿Se identificó un error concreto?
4. ¿Se aplicó una corrección real?
5. ¿Hay hipótesis para la próxima sesión?

CRITERIO POR DOMINIO:
- Si el dominio es técnico (programación, música, deporte):
  evaluar especificidad técnica del error y corrección.
- Si el dominio es blando (escritura, liderazgo, arte):
  evaluar especificidad CONCEPTUAL. No exijas tecnicismo
  donde no existe. El error puede ser de percepción,
  enfoque, o intención.

Responde ÚNICAMENTE en JSON con este esquema exacto:
{
  "was_deliberate": bool,
  "score": 1-100,
  "confidence": 0.0-1.0,
  "verdict": "string corto",
  "reasoning": "string con explicación",
  "domain_specific_notes": "string opcional — notas del dominio",
  "book_citations": ["Peak cap.X: ...", ...]
}

No incluyas texto fuera del JSON. Nunca.
```

---

## Indexación de Libros (NUEVO en v4.0)

NO se indexan al iniciar el backend. Comando separado:

```bash
peak index-books          # Indexa TODOS los PDFs en books/
peak index-books --watch  # Opcional: watchdog que indexa al agregar
```

Cada PDF nuevo en `/books` se indexa manualmente con este comando. El sistema se vuelve más inteligente sin tocar código.

**ChromaDB:** `persist_directory` configurado desde el día 1. Versión de LlamaIndex fijada en `requirements.txt`.

---

## Fases de Construcción

| Fase | Entregable | Tiempo |
|------|-----------|--------|
| **1** | CRUD Skills + Sessions + Dashboard. Sin IA. 100% funcional. Modelo de datos completo desde el vamos (incluyendo campos Quick Log). | 2 semanas |
| **2** | LM Studio integrado. Prompt del Auditor. Pydantic validation. Onboarding mode. Quick Log flow + background AI. | 1 semana |
| **3** | RAG: libros → chunks → ChromaDB → citas en feedback. Comando `peak index-books`. | 1 semana |
| **4** | MentalRep versionado + triggers automáticos + comparación IA | 1 semana |
| **5** | Claude como oráculo (fallback) + API Key auth (o JWT) | 1 semana |

---

## Errores Críticos a Evitar

| # | Error | Solución |
|---|-------|---------|
| 1 | API key en frontend | Siempre via backend, sin excepción |
| 2 | JSON inválido de LM Studio | Forzar en prompt + Pydantic en cada response. Reintentar 1 vez |
| 3 | ChromaDB sin persistencia | `persist_directory` configurado desde día 1 |
| 4 | LlamaIndex breaking changes | Fijar versión exacta en `requirements.txt` desde inicio |
| 5 | Rechazos sin explicación | `reasoning` + `book_citations` siempre visibles en UI |
| 6 | Habilidades blandas sin criterio | Prompt diferenciado por `domain` de la Skill (v4.0) |
| 7 | MentalRep sin estructura | UI fuerza formato: "Antes veía _ / Ahora veo _" |
| 8 | Validación solo en frontend | Validar campos obligatorios en frontend Y FastAPI |
| 9 | LM Studio apagado sin manejo | Backend detecta falla → intenta Claude → error claro en UI. Quick Log fields quedan `pending` |
| 10 | **UX post-sesión con fricción** (NUEVO) | Quick Log con 3 campos + IA completa en background. La entrada de datos debe ser rápida cuando estás cansado |

---

## Principios de Diseño UX (Post-Sesión)

- **La fatiga es real.** Después de practicar, el usuario no quiere pensar. Priorizá velocidad sobre completitud.
- **El modo Quick es el default.** Full existe, pero no es el camino feliz.
- **La IA trabaja para vos.** Si podés delegarle un campo, delega.
- **Todo campo completado por IA es editable.** El usuario siempre tiene la última palabra.
- **Feedback asíncrono.** El resultado de la auditoría puede llegar segundos después de guardar la sesión. No bloquees la UI.
