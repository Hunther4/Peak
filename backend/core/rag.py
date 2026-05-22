"""
RAG Pipeline para Peak — Fase 3
Indexa PDFs de books/ en ChromaDB via LlamaIndex + HuggingFace embeddings.
NO se ejecuta al arrancar el backend. Solo por CLI o endpoint manual.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# --- Paths ---
BACKEND_DIR = Path(__file__).parent.parent
BOOKS_DIR = BACKEND_DIR.parent / "books"
CHROMA_DIR = BACKEND_DIR / "chroma_data"
COLLECTION_NAME = "peak_books"
METADATA_FILE = CHROMA_DIR / "index_metadata.json"

# --- Estado global de indexación (para el endpoint /status) ---
import threading
_is_indexing: bool = False
_indexing_lock = threading.Lock()

_embed_model = None
def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        _embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _embed_model


_chroma_client = None


def _get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        from chromadb.config import Settings
        _chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    return _chroma_client


def _load_metadata() -> dict:
    """Carga el JSON de metadatos de libros indexados."""
    if METADATA_FILE.exists():
        try:
            return json.loads(METADATA_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_metadata(meta: dict) -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_FILE.write_text(json.dumps(meta, indent=2, default=str))


def has_pdf_files() -> bool:
    """Verifica si hay algún archivo PDF en el directorio de libros."""
    return any(BOOKS_DIR.glob("*.pdf"))


def try_acquire_index_lock() -> bool:
    """
    Intenta adquirir el lock de indexación.
    Retorna True si se adquirió (puede comenzar a indexar).
    Retorna False si ya hay una indexación en curso.
    """
    global _is_indexing
    if _indexing_lock.acquire(blocking=False):
        if _is_indexing:
            _indexing_lock.release()
            return False
        _is_indexing = True
        _indexing_lock.release()
        return True
    return False


def release_index_lock():
    """Libera el lock de indexación."""
    global _is_indexing
    with _indexing_lock:
        _is_indexing = False


def index_books(force_reindex: bool = False) -> dict:
    """
    Escanea books/ e indexa cada PDF nuevo en ChromaDB.
    Si force_reindex=True, borra la colección y re-indexa todo.
    Retorna un resumen de lo que se hizo.
    """
    global _is_indexing

    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core import StorageContext
    from llama_index.core import Settings as LISettings

    with _indexing_lock:
        _is_indexing = True
    indexed = []
    skipped = []

    try:
        BOOKS_DIR.mkdir(parents=True, exist_ok=True)
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

        pdf_files = list(BOOKS_DIR.glob("*.pdf"))
        if not pdf_files:
            return {"indexed": [], "skipped": [], "message": "No hay PDFs en books/"}

        metadata = _load_metadata()

        # Si force_reindex, limpiamos la colección y el metadata
        chroma_client = _get_chroma_client()
        if force_reindex:
            try:
                chroma_client.delete_collection(COLLECTION_NAME)
            except Exception as e:
                logger.warning("Error deleting collection: %s", e)
            metadata = {}

        collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

        # Configurar embeddings HuggingFace (CPU, 33MB)
        embed_model = _get_embed_model()
        LISettings.embed_model = embed_model
        LISettings.llm = None  # No usamos LLM aquí

        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_ctx = StorageContext.from_defaults(vector_store=vector_store)

        for pdf_path in pdf_files:
            source = pdf_path.name
            book_title = pdf_path.stem.replace("-", " ").replace("_", " ").title()

            # Saltear si ya está indexado y no es force
            if not force_reindex and source in metadata:
                skipped.append(source)
                continue

            try:
                # Cargar PDF
                reader = SimpleDirectoryReader(
                    input_files=[str(pdf_path)],
                )
                documents = reader.load_data()

                if not documents:
                    continue

                # Agregar metadata a cada documento
                for doc in documents:
                    doc.metadata["source"] = source
                    doc.metadata["book_title"] = book_title

                # Parsear en nodos (chunks)
                nodes = splitter.get_nodes_from_documents(documents)
                total_chunks = len(nodes)

                # Agregar chunk_index y total_chunks a cada nodo
                for i, node in enumerate(nodes):
                    node.metadata["chunk_index"] = i
                    node.metadata["total_chunks"] = total_chunks

                # Indexar en ChromaDB
                index = VectorStoreIndex(
                    nodes=nodes,
                    storage_context=storage_ctx,
                )

                # Guardar metadata
                metadata[source] = {
                    "book_title": book_title,
                    "source": source,
                    "chunks_count": total_chunks,
                    "last_indexed": datetime.now(timezone.utc).isoformat(),
                }
                indexed.append(source)
                logger.info("Indexado: %s (%d chunks)", source, total_chunks)

            except Exception as e:
                logger.error("Error indexando %s: %s", source, e)

        _save_metadata(metadata)
        return {"indexed": indexed, "skipped": skipped, "message": f"{len(indexed)} libro(s) indexado(s)."}

    finally:
        with _indexing_lock:
            _is_indexing = False


def query_books(query: str, top_k: int = 3) -> list[dict]:
    """
    Busca en ChromaDB los chunks más relevantes para el query.
    Retorna lista vacía si no hay libros indexados (nunca rompe).
    """
    try:
        if not CHROMA_DIR.exists() or not METADATA_FILE.exists():
            return []

        metadata = _load_metadata()
        if not metadata:
            return []

        embed_model = _get_embed_model()
        LISettings.embed_model = embed_model
        LISettings.llm = None

        chroma_client = _get_chroma_client()

        try:
            collection = chroma_client.get_collection(COLLECTION_NAME)
        except Exception:
            return []

        # Obtener embedding del query
        query_embedding = embed_model.get_query_embedding(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        if not results["documents"] or not results["documents"][0]:
            return []

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # ChromaDB usa distancia L2; convertimos a score 0-1 aproximado
            score = max(0.0, 1.0 - (dist / 2.0))
            chunks.append({
                "text": doc,
                "score": round(score, 4),
                "source": meta.get("source", ""),
                "book_title": meta.get("book_title", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "total_chunks": meta.get("total_chunks", 0),
            })

        return chunks

    except Exception as e:
        logger.error("Error en query_books: %s", e)
        return []


def get_indexed_books() -> list[dict]:
    """
    Devuelve la lista de libros indexados desde el metadata file.
    """
    metadata = _load_metadata()
    return list(metadata.values())


def is_indexing() -> bool:
    """Retorna True si hay una indexación en progreso."""
    return _is_indexing
