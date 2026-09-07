# 🧩 Propuesta de Optimización — Peak Practice (RAG Pipeline)

## ¿Qué es esto?

Este documento es el resultado de un **Judgment Day** (auditoría adversarial con 2 jueces independientes) aplicado al pipeline de RAG Semántico extraído de Peak. Cada cambio propuesto debe ser evaluado por el equipo antes de implementarlo.

---

## ⚠️ Evaluación Previa

Antes de aplicar estos cambios, preguntate:

1. **¿El RAG sigue siendo parte activa de Peak?** Si el proyecto ya no usa ChromaDB o migró a otro proveedor, estos cambios pueden no aplicar.
2. **¿Hay concurrencia real?** Los locks de inicialización solo importan si hay requests simultáneas al endpoint de query.
3. **¿Qué tan críticos son los metadatos?** Si el archivo `index_metadata.json` se pierde, la re-indexación es costosa. El fix atómico previene eso.

---

## 🔍 Hallazgos y Propuestas

### Propuesta A (ALTA): Escritura Atómica de Metadatos
**Problema**: `_save_metadata` escribe directamente al archivo. Un crash durante la escritura corrompe `index_metadata.json`, forzando una re-indexación completa.

**Código Propuesto**:
```python
def _save_metadata(meta: dict) -> None:
    tmp_path = str(METADATA_FILE) + ".tmp"
    Path(tmp_path).write_text(json.dumps(meta, indent=2, default=str))
    os.replace(tmp_path, str(METADATA_FILE))  # Atómico en Linux/Mac
```

### Propuesta B (MEDIA): Thread-Safe Singletons
**Problema**: `_get_embed_model()` y `_get_chroma_client()` pueden inicializarse múltiples veces si dos requests llegan simultáneamente.

**Código Propuesto**:
```python
_embed_model_lock = threading.Lock()
def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        with _embed_model_lock:
            if _embed_model is None:  # Double-checked locking
                _embed_model = HuggingFaceEmbedding(...)
    return _embed_model
```

### Propuesta C (MEDIA): Filtro de Similitud
**Problema**: `query_books` devuelve `top_k` resultados incluso si son irrelevantes (bajo score de similitud), contradiciendo el `Gotcha` del blueprint sobre "Noise Injection".

**Código Propuesto**:
```python
SIMILARITY_THRESHOLD = 0.3
if score < SIMILARITY_THRESHOLD:
    continue  # Descarta chunks irrelevantes
```

---

## 📋 Resumen

| Prioridad | Cambio | Riesgo | Esfuerzo |
|:---|:---|---:|:---:|
| 🔴 Alta | Escritura atómica de metadatos | Corrupción de índice | Bajo |
| 🟡 Media | Thread-safe singletons | Doble inicialización | Bajo |
| 🟡 Media | Filtro de similitud | Noise injection en LLM | Bajo |

*Evaluar antes de implementar. No todos los cambios son necesarios para todos los entornos.*
