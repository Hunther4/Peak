#!/usr/bin/env python3
"""
CLI para gestionar el índice RAG de Peak.

Uso:
  python rag_cli.py index           # Indexa PDFs nuevos en books/
  python rag_cli.py index --force   # Re-indexa todo desde cero
  python rag_cli.py list            # Lista libros indexados
  python rag_cli.py query "texto"   # Busca chunks relevantes
"""
import sys
import json
from pathlib import Path

# Asegurar que el backend está en el path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag import index_books, query_books, get_indexed_books


def cmd_index(force: bool = False) -> None:
    print(f"[RAG] Iniciando indexación... (force={force})")
    result = index_books(force_reindex=force)
    print(f"\n✅ Indexados:  {result['indexed']}")
    print(f"⏭  Saltados:   {result['skipped']}")
    print(f"💬 Mensaje:    {result['message']}")


def cmd_list() -> None:
    books = get_indexed_books()
    if not books:
        print("No hay libros indexados. Ejecutá: python rag_cli.py index")
        return
    print(f"\n📚 Libros indexados ({len(books)}):\n")
    for b in books:
        print(f"  - {b['book_title']}")
        print(f"    Fuente:       {b['source']}")
        print(f"    Chunks:       {b['chunks_count']}")
        print(f"    Indexado:     {b['last_indexed']}")
        print()


def cmd_query(text: str, top_k: int = 3) -> None:
    print(f"\n🔍 Buscando: \"{text}\" (top {top_k})\n")
    results = query_books(text, top_k=top_k)
    if not results:
        print("Sin resultados. Verificá que haya libros indexados.")
        return
    for i, r in enumerate(results, 1):
        print(f"--- Resultado {i} ---")
        print(f"Libro:    {r['book_title']}")
        print(f"Fuente:   {r['source']}")
        print(f"Chunk:    {r['chunk_index']} / {r['total_chunks']}")
        print(f"Score:    {r['score']}")
        print(f"Texto:    {r['text'][:300]}...")
        print()


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    command = args[0]

    if command == "index":
        force = "--force" in args
        cmd_index(force=force)

    elif command == "list":
        cmd_list()

    elif command == "query":
        if len(args) < 2:
            print("Uso: python rag_cli.py query \"tu consulta\"")
            sys.exit(1)
        query_text = args[1]
        top_k = int(args[2]) if len(args) > 2 else 3
        cmd_query(query_text, top_k=top_k)

    else:
        print(f"Comando desconocido: {command}")
        print("Comandos válidos: index, list, query")
        sys.exit(1)


if __name__ == "__main__":
    main()
