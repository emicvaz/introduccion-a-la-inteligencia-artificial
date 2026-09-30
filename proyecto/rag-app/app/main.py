import time
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.chunk import process_document_by_articulo
from app.embed import get_embedding, get_embeddings_batch
from app.store import add_chunks_to_db, query_similar_chunks, get_total_chunks, collection
from app.generate import generate_rag_answer

app = FastAPI(
    title="Sistema RAG - Legislación Yucatán",
    version="1.0.0",
    description="API RAG con FastAPI, ChromaDB y Google AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Esquemas Pydantic ---
class Citation(BaseModel):
    id: str
    source: str
    chunk_index: int
    text: str
    score: float

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3
    sources: Optional[List[str]] = None  # Lista opcional de documentos (ej. ["ley-notarial.md"])

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    abstained: bool


# --- Endpoints ---
@app.get("/health", tags=["Salud"])
def health_check():
    return {
        "status": "ok",
        "chroma_connected": True,
        "total_indexed_chunks": get_total_chunks()
    }


@app.get("/sources", tags=["Consulta"])
def get_available_sources():
    """Devuelve la lista única de documentos normativos indexados en ChromaDB."""
    try:
        data = collection.get(include=["metadatas"])
        unique_sources = set()
        for meta in data.get("metadatas", []):
            if meta and "source" in meta:
                unique_sources.add(meta["source"])
        return {"sources": sorted(list(unique_sources))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener fuentes: {str(e)}")


def _index_chunk_records(chunk_records: list) -> int:
    """Indexa la lista de chunks de un documento en ChromaDB."""
    texts = [c["text"] for c in chunk_records]
    ids = [c["id"] for c in chunk_records]
    metadatas = [c.get("metadata", {"source": c["source"], "chunk_index": c["chunk_index"]}) for c in chunk_records]

    # Genera los vectores en micro-lotes
    embeddings = get_embeddings_batch(texts)

    inserted = add_chunks_to_db(ids, texts, embeddings, metadatas)
    return inserted


@app.post("/ingest", tags=["Ingesta"])
async def ingest_files(files: List[UploadFile] = File(...)):
    """Recibe archivos cargados desde Streamlit o Swagger."""
    total_docs = len(files)
    total_chunks = 0

    for file in files:
        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("latin-1")

        records = process_document_by_articulo(file.filename, content)
        if records:
            inserted = _index_chunk_records(records)
            total_chunks += inserted

    return {
        "message": "Archivos indexados exitosamente",
        "documents_processed": total_docs,
        "chunks_indexed": total_chunks,
        "total_in_collection": get_total_chunks()
    }


@app.post("/ingest-data-folder", tags=["Ingesta"])
def ingest_data_folder():
    """Lee directamente la carpeta data/ e indexa todos los .md y .txt."""
    data_path = Path("./data")
    files = list(data_path.glob("*.md")) + list(data_path.glob("*.txt"))
    
    if not files:
        raise HTTPException(status_code=404, detail="No se encontraron archivos en data/")

    total_chunks = 0
    docs_processed = 0

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        records = process_document_by_articulo(file_path.name, content)
        if not records:
            continue

        inserted = _index_chunk_records(records)
        total_chunks += inserted
        docs_processed += 1

    return {
        "message": "Carpeta data indexada exitosamente",
        "documents_processed": docs_processed,
        "chunks_indexed": total_chunks,
        "total_in_collection": get_total_chunks()
    }


@app.post("/query", response_model=QueryResponse, tags=["Consulta"])
def query_rag(payload: QueryRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    # 1. Vectorizar la pregunta
    query_vector = get_embedding(question)

    # 2. Configurar filtro opcional por documento normativo
    where_filter = None
    if payload.sources:
        if len(payload.sources) == 1:
            where_filter = {"source": payload.sources[0]}
        else:
            where_filter = {"source": {"$in": payload.sources}}

    # 3. Búsqueda k-NN en Chroma con soporte de filtro
    chunks = query_similar_chunks(query_vector, top_k=payload.top_k, where=where_filter)

    # 4. Abstención si los scores son muy bajos
    SIMILARITY_THRESHOLD = 0.40
    if not chunks or chunks[0]["score"] < SIMILARITY_THRESHOLD:
        return QueryResponse(
            answer="No tengo evidencia suficiente para responder a esta pregunta.",
            citations=[],
            abstained=True
        )

    # 5. Generación con Gemini
    answer, abstained = generate_rag_answer(question, chunks)

    citations = [
        Citation(
            id=c["id"],
            source=c["source"],
            chunk_index=c["chunk_index"],
            text=c["text"],
            score=c["score"]
        )
        for c in chunks
    ]

    return QueryResponse(
        answer=answer,
        citations=citations,
        abstained=abstained
    )