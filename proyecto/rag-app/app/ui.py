import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Consultas Jurídicas y Normativas - Yucatán",
    page_icon="⚖️",
    layout="wide",
)

# --- Inicializar historial en sesión ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuración y Estado")

# Verificación de conexión
    try:
        health_resp = requests.get(f"{API_URL}/health", timeout=3)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            st.success("🟢 Backend conectado")
            # Leemos la clave correcta devuelta por FastAPI
            total_chunks = health_data.get("total_indexed_chunks", health_data.get("indexed_chunks", 0))
            st.metric("Total Chunks en Base", total_chunks)
            if total_chunks == 0:
                st.warning("⚠️ No hay documentos indexados. Carga el corpus antes de consultar.")
        else:
            st.warning("🟠 Backend respondió con error")
    except Exception:
        st.error("🔴 Backend desconectado (FastAPI no disponible en el puerto 8000)")

    st.markdown("---")

    top_k = st.slider(
        "Fragmentos a recuperar (top_k):",
        min_value=2,
        max_value=10,
        value=5,
        help="Más fragmentos = respuestas más completas pero más lentas. Para consultas complejas usa 7-10.",
    )

    st.info(
        "El sistema solo responde con base en la evidencia "
        "normativa y se abstiene si no hay sustento suficiente."
    )

    # Botón para limpiar historial
    st.markdown("---")
    if st.button("🗑️ Limpiar historial", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- Encabezado principal ---
st.title("Asesor Normativo Inmobiliario — Yucatán")
st.caption("Sistema RAG especializado con anclaje normativo estricto y citas verificables.")
st.markdown("---")

# --- Área de consulta ---
query = st.text_area(
    "Escribe tu consulta sobre la legislación de Yucatán:",
    placeholder="Ej: ¿Cuáles son las obligaciones del Notario Público en el ejercicio de sus funciones?",
    height=100,
)

submit = st.button("Consultar 🔎", type="primary")

# --- Helpers ---
def score_label(score: float) -> str:
    if score >= 0.75:
        return "🟢 Alta relevancia"
    if score >= 0.62:
        return "🟡 Relevancia media"
    return "🔴 Baja relevancia"


def render_chunk_text(text: str):
    """Separa el prefijo de contexto jerárquico del cuerpo del artículo."""
    if "\n\n" in text:
        context_line, article_body = text.split("\n\n", 1)
        st.caption(context_line)
        st.markdown(article_body)
    else:
        st.markdown(text)


def render_citations(citations: list):
    st.markdown("---")
    st.subheader("📚 Evidencia Normativa Recuperada")
    for idx, c in enumerate(citations, 1):
        score = c.get("score", 0.0)
        source = c.get("source", "Documento")
        chunk_id = c.get("id", "")
        label = score_label(score)
        with st.expander(f"Fragmento [{idx}] — {source}  {label}"):
            st.caption(f"**Identificador:** `{chunk_id}`")
            render_chunk_text(c.get("text", ""))


def render_history():
    previous = st.session_state.history[:-1]  # Excluir la consulta actual
    if not previous:
        return
    with st.expander(f"🕓 Consultas anteriores ({len(previous)})"):
        for h in reversed(previous):
            st.markdown(f"**{h['query']}**")
            st.markdown(h["answer"])
            st.markdown("---")


# --- Lógica principal ---
if submit:
    if not query.strip():
        st.warning("Por favor ingresa una consulta válida.")
    else:
        with st.spinner("Buscando evidencia normativa y generando respuesta..."):
            try:
                payload = {"question": query.strip(), "top_k": top_k}
                res = requests.post(f"{API_URL}/query", json=payload, timeout=120)

                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    citations = data.get("citations", [])
                    abstained = data.get("abstained", False)

                    # Guardar en historial
                    st.session_state.history.append({
                        "query": query.strip(),
                        "answer": answer,
                        "citations": citations,
                        "abstained": abstained,
                    })

                    st.markdown("### 📋 Respuesta")

                    if abstained:
                        st.warning(answer)
                        st.info(
                            "💡 Sugerencia: reformula la consulta siendo más específico, "
                            "o aumenta el número de fragmentos a recuperar en el panel lateral."
                        )
                    else:
                        st.markdown(answer)

                    if citations:
                        render_citations(citations)

                else:
                    st.error(f"Error en la consulta (HTTP {res.status_code}): {res.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"No fue posible comunicarse con el servicio FastAPI: {e}")

# --- Historial de consultas anteriores ---
if len(st.session_state.history) > 1:
    render_history()