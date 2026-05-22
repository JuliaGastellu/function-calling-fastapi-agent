from .calculator_tool import calculate, CALCULATOR_SCHEMA
from .rag_tool import search_documents, RAG_SCHEMA
from .orders_tool import get_order, list_orders, GET_ORDER_SCHEMA, LIST_ORDERS_SCHEMA
from .hours_tool import get_hours, HOURS_SCHEMA

# Lista unificada de esquemas JSON para registro en el SDK de OpenAI
ALL_TOOLS = [
    CALCULATOR_SCHEMA,
    RAG_SCHEMA,
    GET_ORDER_SCHEMA,
    LIST_ORDERS_SCHEMA,
    HOURS_SCHEMA,
]

# Mapa de nombres de herramientas a sus respectivas funciones ejecutables
TOOL_FUNCTIONS = {
    "calculate": calculate,
    "search_documents": search_documents,
    "get_order": get_order,
    "list_orders": list_orders,
    "get_hours": get_hours,
}
