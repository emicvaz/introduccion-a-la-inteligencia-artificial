from app.chunk import process_document_to_chunks
from app.embed import get_embeddings_batch, get_embedding
from app.store import add_chunks_to_db, query_similar_chunks, get_total_chunks

print("--- 1. Probando Chunking ---")
texto_ejemplo = """
El Notario Público en Yucatán tiene la obligación de verificar la identidad de las partes
comparecientes, solicitar el certificado de libertad de gravamen emitido por el Registro
Público de la Propiedad, y retener los impuestos correspondientes como el ISAI y el ISR.
Para la compraventa de bienes inmuebles en Mérida, se requiere presentar la cédula catastral
actualizada y el plano del predio.
""" * 5

chunks_data = process_document_to_chunks("prueba_notarial.md", texto_ejemplo, chunk_size=40, overlap=10)
print(f"Total chunks generados: {len(chunks_data)}")
print(f"Ejemplo ID: {chunks_data[0]['id']}")

print("\n--- 2. Probando Google AI Embeddings en Lote ---")
textos = [c["text"] for c in chunks_data]
embeddings = get_embeddings_batch(textos)
print(f"Embeddings calculados: {len(embeddings)} vectores")
print(f"Dimensión del primer vector: {len(embeddings[0])} (Esperado: 768)")

print("\n--- 3. Probando Inserción y Persistencia en ChromaDB ---")
ids = [c["id"] for c in chunks_data]
metas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks_data]
insertados = add_chunks_to_db(ids, textos, embeddings, metas)
print(f"Chunks insertados en la BD: {insertados}")
print(f"Total documentos en la colección: {get_total_chunks()}")

print("\n--- 4. Probando Consulta Semántica k-NN ---")
pregunta = "¿Qué documentos solicita el notario para la compraventa?"
q_vec = get_embedding(pregunta)
resultados = query_similar_chunks(q_vec, top_k=2)

for i, res in enumerate(resultados, 1):
    print(f"\n[Resultado {i}]")
    print(f"Fuente: {res['source']} | Score similitud: {res['score']}")
    print(f"Texto: {res['text'][:120]}...")

print("\n Fase 2 completada exitosamente.")