"""
Tests for the RAG pipeline — validation and edge-cases only.

No real PDFs, no real ChromaDB initialization needed for these basic checks.
All RAG functions gracefully return empty results when no books are indexed.
"""


# We assume the app is imported or configured in conftest.py
# Since we are writing the file, we will use the 'client' fixture provided by the environment

from unittest.mock import patch


def test_index_books_no_files_returns_400(client):
    """POST /api/books/index should return 400 if no PDFs are found in books/"""
    with patch("api.routes.books.has_pdf_files", return_value=False):
        response = client.post("/api/books/index", json={"force": False})
        assert response.status_code == 400
        assert response.json()["detail"] == "No hay archivos PDF en la carpeta books/ para indexar."


def test_status_empty_when_no_books_indexed(client):
    """GET /api/books/status should show empty books list when nothing indexed"""
    with patch("api.routes.books.is_indexing", return_value=False):
        response = client.get("/api/books/status")
        assert response.status_code == 200
        data = response.json()
        assert data["books"] == []
        assert data["total_chunks"] == 0
        assert data["is_indexing"] is False

def test_search_rag_no_books_returns_empty(client):
    """GET /api/books/search should return empty results when no books indexed"""
    response = client.get("/api/books/search", params={"q": "test query"})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test query"
    assert data["results"] == []
    assert data["count"] == 0

def test_search_rag_empty_query_returns_400(client):
    """GET /api/books/search with empty q should return 400"""
    response = client.get("/api/books/search", params={"q": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "El parámetro 'q' no puede estar vacío."

def test_index_books_no_body_returns_validation_error(client):
    """POST /api/books/index without body should return 422"""
    response = client.post("/api/books/index")
    assert response.status_code == 422
