from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb

# Ruta persistente local exigida por el proyecto
CHROMA_PATH = Path("./chroma").resolve()

# Inicializar cliente persistente
client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# Creamos o recuperamos la colección configurando distancia coseno
collection = client.get_or_create_collection(
    name="rag_corpus",
    metadata={"hnsw:space": "cosine"}
)


def add_chunks_to_db(
    ids: List[str],
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict[str, Any]]
) -> int:
    """
    Inserta o actualiza chunks con sus vectores y metadatos en ChromaDB.
    Se usa 'upsert' para evitar errores si se indexa el mismo documento dos veces.
    """
    if not ids:
        return 0

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    return len(ids)


def query_similar_chunks(
    query_embedding: List[float], 
    top_k: int = 3, 
    where: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Busca los k chunks más cercanos al vector de la pregunta.
    Permite filtrar por metadatos (ej. source) usando la cláusula where.
    """
    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"]
    }
    if where:
        query_kwargs["where"] = where

    results = collection.query(**query_kwargs)

    if not results or not results["ids"] or not results["ids"][0]:
        return []

    ids = results["ids"][0]
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    chunks = []
    for i in range(len(ids)):
        dist = distances[i] if distances is not None else 1.0
        score = max(0.0, 1.0 - dist)
        meta = metas[i] if metas and metas[i] else {}
        chunks.append({
            "id": ids[i],
            "source": meta.get("source", "desconocido"),
            "chunk_index": meta.get("chunk_index", 0),
            "text": docs[i],
            "score": round(score, 4)
        })

    return chunks


def get_total_chunks() -> int:
    """Devuelve la cantidad de chunks indexados actualmente."""
    return collection.count()