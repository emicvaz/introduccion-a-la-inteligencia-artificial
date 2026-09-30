import re
from pathlib import Path
from typing import List, Dict, Any


def extract_hierarchy(text_before: str) -> Dict[str, str]:
    """
    Extrae el contexto jerárquico activo (libro, título, capítulo, sección)
    recorriendo las líneas previas al artículo.
    """
    hierarchy = {}
    patterns = {
        "libro":    r'^#+\s*LIBRO\s+.+',
        "titulo":   r'^#+\s*T[ÍI]TULO\s+.+',
        "capitulo": r'^#+\s*CAP[ÍI]TULO\s+.+',
        "seccion":  r'^#+\s*SECCI[ÓO]N\s+.+',
    }

    # Recorremos línea por línea; el último encabezado visto sobreescribe el anterior
    for line in text_before.split("\n"):
        line_clean = line.strip()
        for key, pattern in patterns.items():
            if re.match(pattern, line_clean, re.IGNORECASE):
                hierarchy[key] = re.sub(r'^[#*_\s]+', '', line_clean).strip('*_ ')

    return hierarchy


def split_large_article(text: str, max_words: int = 400, overlap: int = 50) -> List[str]:
    """Divide artículos extraordinariamente largos preservando solape."""
    words = text.split()
    if len(words) <= max_words:
        return [text]

    chunks = []
    step = max_words - overlap
    for i in range(0, len(words), step):
        sub_chunk = " ".join(words[i : i + max_words]).strip()
        if sub_chunk:
            chunks.append(sub_chunk)
        if i + max_words >= len(words):
            break
    return chunks


def split_by_articulo(text: str) -> List[Dict[str, Any]]:
    """
    Identifica el inicio de los artículos tolerando negritas, encabezados o texto plano.
    Ejemplos soportados:
    - **Artículo 1.**
    - ### Artículo 15.-
    - Art. 24
    """
    # Regex flexible: acepta inicio de línea opcionalmente seguido de #, *, _, espacios
    pattern = re.compile(
        r'(?:^|\n)\s*(?:[#*_\s]*)(?:art[íi]culo|art\.)\s+(\d+[\w\-\.]*)',
        re.IGNORECASE
    )

    matches = list(pattern.finditer(text))
    if not matches:
        return []

    chunks = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        article_text = text[start:end].strip()
        hierarchy = extract_hierarchy(text[:start])

        # Si el artículo excede 450 palabras, lo subdividimos
        sub_parts = split_large_article(article_text, max_words=450, overlap=50)

        for part_idx, part_text in enumerate(sub_parts):
            chunks.append({
                "text": part_text,
                "hierarchy": hierarchy,
                "sub_idx": part_idx
            })

    return chunks


def process_document_by_articulo(
    filename: str, content: str
) -> List[Dict[str, Any]]:
    """
    Procesa el documento legal generando chunks con el prefijo jerárquico
    y metadatos seguros para ChromaDB.
    """
    raw_chunks = split_by_articulo(content)
    records = []
    stem = Path(filename).stem

    # Fallback si el texto no contiene la palabra Artículo (ej. introducción o glosario)
    if not raw_chunks:
        words = content.split()
        step = 300 - 50
        for idx, i in enumerate(range(0, len(words), step)):
            chunk_txt = " ".join(words[i : i + 300])
            if chunk_txt.strip():
                records.append({
                    "id": f"{stem}_chunk_{idx:04d}",
                    "text": f"[Documento: {stem}]\n\n{chunk_txt}",
                    "source": filename,
                    "chunk_index": idx
                })
        return records

    for idx, chunk in enumerate(raw_chunks):
        h = chunk["hierarchy"]

        # Construir breadcrumb contextual
        context_parts = [f"[Documento: {stem}]"]
        if h.get("libro"):
            context_parts.append(f"[{h['libro']}]")
        if h.get("titulo"):
            context_parts.append(f"[{h['titulo']}]")
        if h.get("capitulo"):
            context_parts.append(f"[{h['capitulo']}]")
        if h.get("seccion"):
            context_parts.append(f"[{h['seccion']}]")

        breadcrumb = " > ".join(context_parts)
        full_text = f"{breadcrumb}\n\n{chunk['text']}"

        # Filtrar metadatos para que ChromaDB no falle con valores vacíos
        safe_metadata = {
            "source": filename,
            "chunk_index": idx
        }
        for k, v in h.items():
            if v:
                safe_metadata[k] = str(v)

        records.append({
            "id": f"{stem}_art_{idx:04d}",
            "text": full_text,
            "source": filename,
            "chunk_index": idx,
            "metadata": safe_metadata
        })

    return records