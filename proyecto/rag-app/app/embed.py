import os
import time
import re
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("No se encontró GOOGLE_API_KEY en el archivo .env")

client = genai.Client(api_key=api_key)
DEFAULT_EMBED_MODEL = "gemini-embedding-001"


def _extract_retry_delay(error_str: str) -> float:
    """Extrae los segundos sugeridos de espera de la respuesta de Google si existen."""
    match = re.search(r'retry in ([\d\.]+)s', error_str)
    if match:
        return float(match.group(1)) + 1.5
    return 15.0


def get_embedding(text: str, model: str = DEFAULT_EMBED_MODEL, max_retries: int = 6) -> List[float]:
    """Genera vector embedding para una consulta individual."""
    for attempt in range(max_retries):
        try:
            response = client.models.embed_content(
                model=model,
                contents=text,
            )
            return response.embeddings[0].values
        except ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait_sec = _extract_retry_delay(str(e))
                print(f"[Cuota 429] Esperando {wait_sec:.1f}s antes de reintentar...")
                time.sleep(wait_sec)
            else:
                raise e


def get_embeddings_batch(
    texts: List[str], 
    model: str = DEFAULT_EMBED_MODEL, 
    sub_batch_size: int = 15, 
    max_retries: int = 6
) -> List[List[float]]:
    """
    Envía textos en micro-lotes de 15 elementos.
    Si la API devuelve 429, aguarda la ventana indicada y reintenta.
    """
    if not texts:
        return []

    all_embeddings = []

    for i in range(0, len(texts), sub_batch_size):
        chunk_group = texts[i : i + sub_batch_size]
        success = False

        for attempt in range(max_retries):
            try:
                response = client.models.embed_content(
                    model=model,
                    contents=chunk_group,
                )
                group_vectors = [e.values for e in response.embeddings]
                all_embeddings.extend(group_vectors)
                success = True
                time.sleep(1.2)  # Pausa de seguridad entre micro-lotes
                break
            except ClientError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    wait_sec = _extract_retry_delay(str(e))
                    print(f"[Cuota 429] Ventana saturada. Esperando {wait_sec:.1f}s para continuar...")
                    time.sleep(wait_sec)
                else:
                    raise e

        if not success:
            raise RuntimeError(f"No fue posible procesar el lote en el índice {i}")

    return all_embeddings