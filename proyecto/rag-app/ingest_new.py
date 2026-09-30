import os
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

from app.chunk import process_document_by_articulo
from app.store import collection, add_chunks_to_db

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
EMBED_MODEL = "gemini-embedding-001"


def get_embedding_with_retry(text: str, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            res = client.models.embed_content(model=EMBED_MODEL, contents=text)
            return res.embeddings[0].values
        except ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                match = re.search(r"retry in ([\d\.]+)s", str(e))
                wait = float(match.group(1)) + 1.0 if match else 20.0
                print(f"[Aviso 429] Esperando {wait:.1f}s...")
                time.sleep(wait)
            else:
                raise e


def ingest_incremental():
    data_dir = Path("data")
    files = sorted(list(data_dir.glob("*.md")) + list(data_dir.glob("*.txt")))

    # 1. Obtener los IDs que ya están guardados en ChromaDB
    existing_records = collection.get()
    existing_ids = set(existing_records.get("ids", []))
    print(f"📊 Chunks actualmente en ChromaDB: {len(existing_ids)}")

    # 2. Particionar todos los archivos en data/
    pending_chunks = []
    for f in files:
        content = f.read_text(encoding="utf-8")
        records = process_document_by_articulo(f.name, content)
        for r in records:
            if r["id"] not in existing_ids:
                pending_chunks.append(r)

    print(f"🆕 Chunks nuevos detectados para indexar: {len(pending_chunks)}")

    if not pending_chunks:
        print("✅ No hay documentos nuevos por indexar. La base ya está al día.")
        return

    # 3. Vectorizar e insertar únicamente los nuevos
    for i, chunk in enumerate(pending_chunks, 1):
        print(f"[{i}/{len(pending_chunks)}] Indexando: {chunk['id']} ...", end="", flush=True)
        vector = get_embedding_with_retry(chunk["text"])

        add_chunks_to_db(
            ids=[chunk["id"]],
            texts=[chunk["text"]],
            embeddings=[vector],
            metadatas=[chunk.get("metadata", {"source": chunk["source"]})],
        )
        print(" ✓")
        time.sleep(0.8)  # Control de ritmo preventivo

    print(f"\n🎉 ¡Listo! Total acumulado en ChromaDB: {collection.count()} chunks.")


if __name__ == "__main__":
    ingest_incremental()