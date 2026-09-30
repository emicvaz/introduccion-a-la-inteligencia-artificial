import os
import time
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("No se encontró GOOGLE_API_KEY en el entorno.")

client = genai.Client(api_key=api_key)

# Modelos confirmados activos en tu cuenta
CANDIDATE_MODELS = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
]

SYSTEM_PROMPT = """Eres un asistente legal y normativo especializado en la legislación y reglamentación de Yucatán.
Tu tarea es responder la pregunta del usuario basándote ÚNICAMENTE en la evidencia provista en los fragmentos de contexto.

REGLAS ESTRICTAS:
1. Responde siempre en español formal y claro.
2. Cada afirmación o dato que des DEBE citar explícitamente la fuente usando el número de fragmento entre corchetes, por ejemplo [1], [2] o [1][2].
3. NO uses conocimientos previos ni asumas nada que no esté explícito en los fragmentos.
4. Si la evidencia no contiene información suficiente para responder con certeza y totalidad a la pregunta, debes ABSTENERTE de responder e incluir exactamente la frase: "No tengo evidencia suficiente para responder a esta pregunta." No inventes ni especules.
"""


def build_context_string(chunks: List[Dict[str, Any]]) -> str:
    """Formatea la lista de chunks como bloques numerados [1], [2]..."""
    context_lines = []
    for idx, c in enumerate(chunks, 1):
        fuente = c.get("source", "desconocida")
        texto = c.get("text", "")
        context_lines.append(f"[{idx}] (Fuente: {fuente}):\n{texto}")
    return "\n\n".join(context_lines)


def generate_rag_answer(question: str, context_chunks: List[Dict[str, Any]]) -> Tuple[str, bool]:
    """
    Genera la respuesta anclada usando Gemini con rotación automática si hay saturación.
    Devuelve: (texto_respuesta, se_abstuvo)
    """
    if not context_chunks:
        return "No tengo evidencia suficiente para responder a esta pregunta.", True

    context_str = build_context_string(context_chunks)
    user_message = f"Evidencia disponible:\n{context_str}\n\nPregunta del usuario:\n{question}"

    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                )
            )
            answer = response.text.strip() if response.text else "No tengo evidencia suficiente para responder a esta pregunta."
            abstained = "no tengo evidencia suficiente" in answer.lower()
            return answer, abstained
        except (ServerError, ClientError) as e:
            last_error = e
            # Si hay congestión temporal (503) o error de versión, intenta con el siguiente modelo de la lista
            time.sleep(1.0)
            continue

    if last_error:
        raise last_error

    return "No tengo evidencia suficiente para responder a esta pregunta.", True