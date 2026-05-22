"""
Endpoints de gestión de libros RAG.
Registrado en main.py como: prefix="/api/books", tags=["Books"]
"""
import logging
from core.tasks import background_executor
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional

from core.rag import index_books, query_books, get_indexed_books, is_indexing, try_acquire_index_lock, release_index_lock, has_pdf_files
from core.limiter import limiter, get_rate_limit_str

logger = logging.getLogger(__name__)

router = APIRouter()

# Usamos el background_executor global de core.tasks


class IndexRequest(BaseModel):
    force: bool = False


@router.post("/index")
@limiter.limit(get_rate_limit_str())
def trigger_indexing(request: Request, body: IndexRequest):
    """
    Lanza la indexación de PDFs en background via ThreadPoolExecutor.
    Responde inmediatamente — no bloquea.
    Usa try_acquire_index_lock para evitar TOCTOU race condition
    entre el chequeo y el submit.
    """
    if not has_pdf_files():
        raise HTTPException(status_code=400, detail="No hay archivos PDF en la carpeta books/ para indexar.")

    if not try_acquire_index_lock():
        return {"status": "already_indexing", "message": "Ya hay una indexación en progreso."}

    try:
        background_executor.submit(index_books, body.force)
    except Exception as e:
        release_index_lock()
        raise HTTPException(status_code=500, detail=f"No se pudo iniciar la tarea en background: {e}")

    return {
        "status": "indexing",
        "message": "Indexación iniciada en background. Consultá /api/books/status para ver el progreso.",
    }


@router.get("/status")
def get_books_status():
    """
    Devuelve el estado del índice: libros indexados, total de chunks, y si está indexando.
    """
    books = get_indexed_books()
    total_chunks = sum(b.get("chunks_count", 0) for b in books)
    return {
        "books": books,
        "total_chunks": total_chunks,
        "is_indexing": is_indexing(),
    }


@router.get("/search")
def search_books(
    q: str = Query(..., max_length=500),
    top_k: int = Query(default=3, le=50),
):
    """
    Busca en los libros indexados y devuelve los chunks más relevantes.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="El parámetro 'q' no puede estar vacío.")

    results = query_books(q.strip(), top_k=top_k)
    return {"query": q, "results": results, "count": len(results)}
