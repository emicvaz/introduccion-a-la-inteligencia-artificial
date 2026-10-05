# Sistema RAG Normativo e Inmobiliario — Yucatán

Sistema integral de **Generación Aumentada por Recuperación (RAG)** para la consulta de la legislación del Estado de Yucatán en materia inmobiliaria, especificamente la ciudad de Mérida y zonas conurbadas.

## Motivación

La ciudad de Mérida está atravesando una de las etapas de mayor expansión urbana de su historia. Esto exige el cumplimiento de varias normas locales: desde autorizaciones y licencias, hasta la certeza registral ante el Instituto de Seguridad Patrimonial del Estado de Yucatán (INSEJUPY) y las obligaciones notariales.

Ante este marco legal, los profesionales del sector inmobiliario enfrentan barreras de consulta técnica y una falta de asesoría jurídica de primer contacto. Los Large Language Models (LLMs) convencionales fallan en este ámbito ya que se entrenan principalmente con datos de internet y carecen de una "conciencia" geográfica sobre las normativas locales de cada jurisdicción, igualmente, tienden a inventar o alucinar articulados. Este sistema RAG nace para resolver esta problemática, ofreciendo un canal de consulta ágil y de alta fidelidad que responde con un sustento normativo los artículos y citaciones explícitas a las leyes de Yucatán (el corpus).

El desarrollo del proyecto final se desacopla de la siguiente manera, cliente-servidor: interfaz web en **Streamlit**, API REST en **FastAPI**, base vectorial persistente en **ChromaDB**, y vectorización/generación con modelos de **Google AI (Gemini)**.

## 1. Arquitectura del Sistema

El flujo respeta una separación estricta donde la interfaz de usuario nunca se comunica directamente con la base vectorial ni con los servicios de Google AI:

```
Usuario (Navegador)
      │
      ▼
Streamlit (Puerto 8501: app/ui.py)
      │  HTTP JSON (requests)
      ▼
FastAPI (Puerto 8000: app/main.py)
      ├── Google AI (gemini-embedding-001) → Vectorización de preguntas y chunks
      ├── ChromaDB (./chroma)              → Persistencia HNSW y búsqueda k-NN (coseno)
      └── Google AI (gemini-flash-latest)  → Generación anclada con citas obligatorias [n]
```

## 2. Estructura del Repositorio

```text
rag-app/
├── app/
│   ├── __init__.py
│   ├── chunk.py          # Partición por artículos y extracción jerárquica
│   ├── embed.py          # Cliente Google AI Embeddings
│   ├── store.py          # Persistencia en ChromaDB utilizando búsqueda k-NN
│   ├── generate.py       # Orquestación LLM Gemini, prompt de sistema y abstención
│   ├── main.py           # API REST FastAPI 
│   └── ui.py             # Aplicación web en Streamlit
├── data/                 # Corpus en formato Markdown (.md)
├── chroma/               # Persistencia de ChromaDB (en .gitignore)
├── requirements.txt      # Dependencias del proyecto
├── .env.example          # Variables de Entorno
├── .gitignore            # Exclusión de entornos, cachés, .env y ./chroma
└── README.md             # Documentación
```

## 3. Corpus Legal y Normativo

El corpus está compuesto por **6 documentos legales reales y vigentes** del Estado de Yucatán y regulación vinculada, estructurados en formato Markdown, tomando en cuenta las ventajas de hacerlo así por la jerarquización de la información:

1. **Ley del Notariado del Estado de Yucatán** 
2. **Reglamento de Construcciones del Municipio de Mérida**
3. **Código de Buenas Prácticas Inmobiliarias**
4. **Ley de Desarrollos Inmobiliarios de Yucatán** 
5. **Ley de Asentamientos Humanos del Estado de Yucatán**  
6. **Ley Federal para la Prevención de Operaciones con Recursos de Procedencia Ilícita** 

* **Volumen:** Aproximadamente 3,000 fragmentos procesados y vectorizados

## 4. Decisiones de Diseño 

La arquitectura técnica del sistema se diseñó bajo criterios de rigor jurídico

### Partición Semántica Legal (`app/chunk.py`)
Los métodos estándar de procesamiento dividen el texto en bloques de tamaño uniforme basados en conteo ciego de tokens o caracteres (por ejemplo, bloques de 500 caracteres). En lugar de esto, el sistema utiliza **chunking por artículo**:
* **Supuesto:** Detección de patrones regex para artículos (`Art.`, `Artículo X`). Pretendiendo que cada chunk sea un artículo.
* **Preservación jerárquica (*Breadcrumbs*):** Cada artículo retiene el contexto de su ubicación estructural: `[Documento] > [Título] > [Capítulo] > [Sección]`.
* **Manejo de artículos extensos:** Artículos de longitud superior a 450 palabras se subdividen con una ventana de 400 palabras y un solape (*overlap*) de 50 palabras para garantizar continuidad semántica.

### Control de Tasa de API (*Rate Limiting*) (`app/embed.py`)
Para operar de manera continua bajo uso gratuito de Google AI Studio sin interrumpir la ingesta:

* Mitigar las cuotas del nivel gratuito: El nivel de evaluación de la API impone un límite de 1,000 de peticiones diarias. Realizar una llamada HTTP por cada uno de los más de 3,000 chunks provocaría el agotamiento inmediato de la cuota diaria. Por lo que la vectorización del corpus tomó 3 días.
* Procesamiento mediante **micro-lotes** (15 a 40 textos por petición HTTP).
* Detección automatizada de respuestas `HTTP 429` extrayendo el tiempo de espera recomendado (`retry in Xs`) y aplicando pausas antes de reintentar.

### Búsqueda Vectorial y Persistencia (`app/store.py`)
* Configuración de la colección con métrica de la distancia coseno: `{"hnsw:space": "cosine"}`.
* Mapeo de similitud lineal con un: $\text{score} = \max(0.0, 1.0 - \text{distancia})$.
* Indexación mediante operaciones `upsert`.
* Capacidad de filtrado por metadatos (`where={"source": ...}`) para acotar búsquedas a leyes particulares.

### Generación Anclada y Protocolo de Abstención (`app/generate.py`)
El modelo opera con temperatura baja ($0.1$) bajo una política estricta de dos niveles:
1. **Filtro de Similitud Mínima:** Si el chunk con mejor puntaje en ChromaDB no supera un umbral mínimo de relevancia ($\text{score} < 0.40$), la API omite la llamada al LLM y devuelve abstención inmediata.
2. **Abstención Textual:** Si la información recuperada no da sustento completo a la pregunta, el prompt prohíbe el uso de conocimiento paramétrico y obliga a responder exactamente:  
   `"No tengo evidencia suficiente para responder a esta pregunta."`, marcando `abstained: true`.

* Ante congestiones temporales o errores de disponibilidad de servicio (HTTP 503) en la API de inferencia, generate_rag_answer itera de forma secuencial sobre una lista jerárquica de modelos (gemini-flash-latest, gemini-flash-lite-latest, gemini-3.5-flash-lite, gemini-3.5-flash) antes de elevar una excepción al cliente.

## 5. Instalación y Puesta en Marcha

### 5.1 Requisitos Previos
* Python 3.9 o superior.
* Clave de API de Google AI Studio.

### 5.2 Configuración del Entorno Virtual

1. Clonar el repositorio y situarse en la carpeta raíz:
   ```bash
   cd rag-app
   ```

2. Crear y activar el entorno virtual de Python:
   ```bash
   # En macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # En Windows:
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instalar las dependencias exactas:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configurar las variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Abre `.env` en tu editor y coloca tu clave:
   ```env
   GOOGLE_API_KEY="TUCLAVEAQUI"
   ```

---

## 6. Ejecución de la Solución

### Paso 1: Levantar el Servidor FastAPI (Backend)
En una terminal con el entorno virtual activo:
```bash
uvicorn app.main:app --reload --port 8000
```
* La documentación interactiva Swagger OpenAPI estará visible en: `http://localhost:8000/docs`.
* El endpoint de salud puede verificarse en: `http://localhost:8000/health`.

### Paso 2: Ingestar el Corpus a ChromaDB
Si es la primera vez que levantas el sistema, ejecuta la ingesta de los documentos ubicados en `data/`:
```bash
curl -X POST "http://localhost:8000/ingest-data-folder"
```


### Paso 3: Levantar la Interfaz en Streamlit (Frontend)
En una **segunda terminal**, con el entorno virtual activo:
```bash
streamlit run app/ui.py
```
La aplicación web se abrirá automáticamente en: `http://localhost:8501`.

---

## 7. Pruebas y Validación de Requisitos

### Prueba 1: Consulta en Dominio con Citación Formal
* **Pregunta:** `¿Cuáles son las obligaciones o facultades del Notario Público según la legislación notarial?`
* **Vía curl:**
  ```bash
  curl -X POST "http://localhost:8000/query" \
       -H "Content-Type: application/json" \
       -d '{"question": "¿Cuáles son las obligaciones o facultades del Notario Público según la legislación notarial?", "top_k": 3}'
  ```
* **Resultado:** Recupera artículos de `ley-notarial.md` con similitud $> 0.77$, generando una respuesta estructurada con citas formales `[1]`, `[2]`, `[3]` y `abstained: false`.

### Prueba 2: Pregunta Fuera de Dominio (Abstención Estricta)
* **Pregunta:** `¿Cuál es la velocidad promedio de traslación del planeta Marte?`
* **Vía curl:**
  ```bash
  curl -X POST "http://localhost:8000/query" \
       -H "Content-Type: application/json" \
       -d '{"question": "¿Cuál es la velocidad promedio de traslación del planeta Marte?", "top_k": 3}'
  ```
* **Resultado:**
  ```json
  {
    "answer": "No tengo evidencia suficiente para responder a esta pregunta.",
    "citations": [...],
    "abstained": true
  }
  ```
* El sistema previene alucinaciones y responde con la frase exacta sin errores 500.

---

## 8. Funcionalidades Adicionales (Retos Opcionales)

* **Filtro selectivo por documento (`sources`):** La API (`POST /query`) y la interfaz en Streamlit admiten seleccionar una o varias leyes específicas para acotar la búsqueda semántica.
* **Historial de conversación interactivo:** La sesión de Streamlit almacena las consultas anteriores con opción de borrado rápido mediante `st.session_state`.
* **Semáforo de relevancia semántica:** La interfaz clasifica visualmente los chunks recuperados (Verde: $\ge 0.75$, Amarillo: $\ge 0.62$, Rojo: $< 0.62$).

## 9. Evidencia

* Evidencia en un video de 3 minutos del funcionamiento de la aplicación.

[![Proyecto RAG: Evidencia de funcionamiento](https://img.youtube.com/vi/KkIpVWMcsTw/mqdefault.jpg)](https://www.youtube.com/watch?v=KkIpVWMcsTw)
