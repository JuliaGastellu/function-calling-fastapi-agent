import os
from pathlib import Path
from typing import Optional
import chromadb
from openai import OpenAI
from config import get_settings

# Variables globales para inicialización diferida (lazy initialization)
_client_chroma: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.api.models.Collection.Collection] = None
_client_openai: Optional[OpenAI] = None


def _init_lazy() -> None:
    """Inicializa de forma diferida las conexiones a ChromaDB y OpenAI."""
    global _client_chroma, _collection, _client_openai

    if _client_chroma is None:
        settings = get_settings()

        # Determinar la ruta absoluta de la base de datos ChromaDB
        directorio_base = Path(__file__).resolve().parents[1]
        ruta_db = directorio_base / settings.chroma_db_path

        # Inicializar clientes
        _client_chroma = chromadb.PersistentClient(path=str(ruta_db))
        _collection = _client_chroma.get_or_create_collection(
            name="cafe_aurora_semantico",
            metadata={"hnsw:space": "l2"}
        )
        _client_openai = OpenAI(api_key=settings.openai_api_key)


def search_documents(query: str) -> str:
    """Busca fragmentos de documentos relevantes en la base de datos de conocimiento de la cafetería.

    Args:
        query (str): Consulta en lenguaje natural a buscar (ej. 'precio de latte de mazapán' o 'vacaciones primer año').

    Returns:
        str: Texto conteniendo los fragmentos de documentos más relevantes y su fuente.
    """
    try:
        _init_lazy()
        assert _client_openai is not None
        assert _collection is not None

        # Generar vector de embedding para la consulta
        respuesta_emb = _client_openai.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        vector_consulta = respuesta_emb.data[0].embedding

        # Consultar la colección
        resultados = _collection.query(
            query_embeddings=[vector_consulta],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )

        documentos = resultados.get("documents", [[]])[0]
        metadatos = resultados.get("metadatas", [[]])[0]

        if not documentos:
            return "No se encontró información relevante sobre esta consulta en los documentos de la cafetería."

        # Formatear la salida estructurada para el agente
        fragmentos_formateados = []
        for doc, meta in zip(documentos, metadatos):
            fuente = meta.get("fuente", "documento") if meta else "documento"
            titulo = meta.get("titulo", "Sin título") if meta else "Sin título"
            fragmentos_formateados.append(f"[{fuente}] ({titulo}):\n{doc}")

        return "\n\n".join(fragmentos_formateados)

    except Exception as e:
        return f"Error al buscar en los documentos de conocimiento (RAG): {str(e)}"


# Esquema JSON compatible con OpenAI Function Calling
RAG_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": "Busca información en los documentos oficiales de Café Aurora (menú, precios, ingredientes, historia, fundadores, políticas de empleado y de la empresa). Úsala para cualquier pregunta de datos internos de la cafetería.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Término de búsqueda o pregunta de la cual recuperar información (ej. 'precio latte mazapán' o 'días de vacaciones')."
                }
            },
            "required": ["query"]
        }
    }
}
