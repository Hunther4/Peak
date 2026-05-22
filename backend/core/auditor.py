import json
import logging
from pydantic import BaseModel, Field
from typing import List, Optional
from core.ai import generate_structured_json
from core.rag import query_books
from core.utils import sanitize_prompt

logger = logging.getLogger(__name__)

class AuditResult(BaseModel):
    was_deliberate: bool
    score: int = Field(ge=1, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    verdict: str
    reasoning: str
    domain_specific_notes: Optional[str] = None
    book_citations: List[str]

def audit_session(session_data: dict, domain: str, onboarding_mode: bool) -> AuditResult:
    """
    Audita una sesión de práctica usando LM Studio.
    Retorna un AuditResult (Pydantic model).
    Si hay libros indexados en ChromaDB, enriquece el prompt con fragmentos relevantes
    y popula book_citations con citas reales.
    """
    # --- Contexto RAG (opcional) ---
    rag_chunks = query_books(session_data.get("what_i_practiced", ""), top_k=3)
    rag_context_block = ""
    real_citations: List[str] = []

    if rag_chunks:
        rag_lines = []
        for chunk in rag_chunks:
            short_text = chunk["text"][:300].replace("\n", " ")
            citation = f"{chunk['book_title']} (chunk {chunk['chunk_index']}): {short_text}"
            real_citations.append(citation)
            rag_lines.append(
                f"Fragmento de referencia:\n{chunk['text']}\n---\nFuente: {chunk['book_title']}"
            )
        rag_context_block = (
            "\n\nCONTEXTO DE LIBROS INDEXADOS (usá estos fragmentos para tus book_citations):\n"
            + "\n\n".join(rag_lines)
            + "\n"
        )

    system_prompt = f"""Eres un auditor estricto de práctica deliberada. Tu única función es evaluar si una sesión cumple los criterios de Anders Ericsson en "Peak".

Criterios de evaluación:
1. ¿El objetivo (what_i_practiced) fue específico y acotado?
2. ¿Estaba en el borde del límite actual (difficulty >= 3)?
3. ¿Se identificó un error concreto (micro_error_found)?
4. ¿Se aplicó una corrección real (correction_applied)?
5. ¿Hay hipótesis para la próxima sesión (hypothesis_tomorrow)?

CRITERIO POR DOMINIO ({domain}):
- Si el dominio es técnico (programación, música, deporte): evaluar especificidad técnica del error y corrección.
- Si el dominio es blando (escritura, liderazgo, arte): evaluar especificidad CONCEPTUAL. No exijas tecnicismo donde no existe. El error puede ser de percepción, enfoque, o intención.

REGLAS DE AUDITORÍA:
- Si falta precisión en 2 o más criterios, was_deliberate DEBE ser false.
- Sé implacable con la vaguedad. "Practiqué piano" es inaceptable. "Practiqué el compás 14-16 prestando atención al pulgar" es aceptable.{rag_context_block}"""

    if onboarding_mode:
        system_prompt += "\n\nMODO ONBOARDING ACTIVO: El usuario está en sus primeras sesiones. Evalúa con honestidad pero con tono educativo. NO modifiques was_deliberate — sé honesto en tu evaluación."

    user_prompt = f"""Sesión a auditar:
- Dominio: {domain}
- Qué practiqué: {sanitize_prompt(session_data.get('what_i_practiced', ''))}
- Dificultad: {session_data.get('difficulty')}/5
- Error encontrado: {sanitize_prompt(session_data.get('micro_error_found', ''))}
- Corrección aplicada: {sanitize_prompt(session_data.get('correction_applied', ''))}
- Hipótesis mañana: {sanitize_prompt(session_data.get('hypothesis_tomorrow', ''))}

Genera tu veredicto."""

    result = generate_structured_json(system_prompt, user_prompt, AuditResult)

    if not result:
        # Fallback seguro en caso de que LM Studio falle o no responda JSON válido
        return AuditResult(
            was_deliberate=False,
            score=1,
            confidence=0.0,
            verdict="Error de Auditoría",
            reasoning="La IA no pudo procesar la auditoría correctamente tras varios reintentos.",
            domain_specific_notes="N/A",
            book_citations=[]
        )

    # Poblar book_citations con citas reales de ChromaDB si las hay.
    # Si la IA generó citas propias pero no hay RAG, se respetan las de la IA.
    # Si hay RAG, reemplazamos con las citas reales indexadas.
    if real_citations:
        result.book_citations = real_citations

    # Onboarding: agregar prefijo al verdict para que la UI lo distinga.
    # NO tocamos was_deliberate (REGLAS-004).
    if onboarding_mode:
        result.verdict = f"[Onboarding] {result.verdict}"

    return result
