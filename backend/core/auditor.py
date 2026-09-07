import logging
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

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

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v):
        if isinstance(v, (int, float)) and v > 1.0:
            return min(1.0, max(0.0, float(v) / 100.0))
        return v

    @field_validator("score", mode="before")
    @classmethod
    def normalize_score(cls, v):
        if isinstance(v, (int, float)):
            return int(round(min(100, max(1, float(v)))))
        return v

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

    system_prompt = """Eres auditor de práctica deliberada (modelo Peak/Anders Ericsson).

CRITERIOS — La sesión es DELIBERADA solo si TODOS se cumplen:
1. OBJETIVO específico: "compás 14-16 piano" ✓ | "practiqué piano" ✗
2. DIFICULTAD ≥ 3/5 (borde del límite actual)
3. MICRO-ERROR concreto: "pulgar llega tarde en negro" ✓ | "me equivoqué" ✗
4. CORRECCIÓN real aplicada: "ralentice 50% y aislé pulgar" ✓ | "practiqué más" ✗
5. HIPÓTESIS mañana: "mañana pruebo metrónomo 60bpm" ✓ | "seguiré practicando" ✗

DOMINIO: """ + domain + """
- Técnico (código, música, deporte): exigi tecnicismo en error/corrección
- Blando (escritura, arte, liderazgo): acepta error conceptual ("enfoqué la audiencia errónea")

REGLAS:
- Si fallan 2+ criterios → was_deliberate: false, score ≤ 30
- Sé implacable: vaguedad = no deliberada
- NO inventes book_citations. Si no hay RAG, devolve [].""" + rag_context_block

    if onboarding_mode:
        system_prompt += "\n\nMODO ONBOARDING: evalúa con honestidad (no cambies was_deliberate), tono educativo."

    user_prompt = f"""AUDITAR SESIÓN:
<user_session_log>
- Dominio: {domain}
- Qué practiqué: {sanitize_prompt(session_data.get('what_i_practiced', ''))}
- Dificultad: {session_data.get('difficulty')}/5
- Error: {sanitize_prompt(session_data.get('micro_error_found', ''))}
- Corrección: {sanitize_prompt(session_data.get('correction_applied', ''))}
- Hipótesis: {sanitize_prompt(session_data.get('hypothesis_tomorrow', ''))}
</user_session_log>

Respondé SOLO el JSON."""

    from core.router import get_ai_mode
    if get_ai_mode() == "api":
        from core.router import execute_with_router
        result = execute_with_router("audit", system_prompt, user_prompt, AuditResult)
    else:
        result = generate_structured_json(system_prompt, user_prompt, AuditResult, force_local=True)


    if not result:
        # Fallback seguro en caso de que la IA falle o no responda JSON válido
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
