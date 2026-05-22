import json
from typing import Optional

# Base de datos simulada de pedidos
BASE_DE_DATOS_PEDIDOS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "sucursal": "Roma Norte",
        "productos": "1x Latte de mazapán, 1x Croissant de mantequilla",
        "total": 112.00,
        "estado": "entregado",
        "fecha": "2026-05-22"
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "sucursal": "Roma Norte",
        "productos": "1x Sándwich de pollo y mostaza suave, 1x Americano",
        "total": 165.00,
        "estado": "en preparación",
        "fecha": "2026-05-22"
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "sucursal": "Condesa",
        "productos": "1x Bizcocho de limón, 1x Té verde",
        "total": 120.00,
        "estado": "en preparación",
        "fecha": "2026-05-22"
    },
    "ORD-004": {
        "order_id": "ORD-004",
        "sucursal": "Juárez",
        "productos": "1x Bocadillo vegetariano con hummus, 1x Cold brew",
        "total": 190.00,
        "estado": "entregado",
        "fecha": "2026-05-22"
    }
}


def get_order(order_id: str) -> str:
    """Consulta la información detallada de un pedido específico por su ID único.

    Args:
        order_id (str): Identificador único del pedido (ej. 'ORD-001').

    Returns:
        str: Representación formateada en JSON del pedido o mensaje de error.
    """
    identificador = order_id.strip().upper()
    pedido = BASE_DE_DATOS_PEDIDOS.get(identificador)
    if not pedido:
        return "Pedido no encontrado"
    return json.dumps(pedido, ensure_ascii=False)


def list_orders(status: Optional[str] = None, branch: Optional[str] = None) -> str:
    """Filtra y lista los pedidos de la cafetería de acuerdo al estado y/o la sucursal de origen.

    Args:
        status (str, opcional): Estado del pedido a filtrar ('entregado' o 'en preparación').
        branch (str, opcional): Nombre de la sucursal a filtrar (ej. 'Roma Norte', 'Condesa', 'Juárez').

    Returns:
        str: Representación formateada en JSON de la lista de pedidos que coinciden con los filtros.
    """
    pedidos_filtrados = []

    for pedido in BASE_DE_DATOS_PEDIDOS.values():
        coincide_estado = True
        coincide_sucursal = True

        if status:
            coincide_estado = pedido["estado"].strip().lower() == status.strip().lower()

        if branch:
            coincide_sucursal = pedido["sucursal"].strip().lower() == branch.strip().lower()

        if coincide_estado and coincide_sucursal:
            pedidos_filtrados.append(pedido)

    return json.dumps(pedidos_filtrados, ensure_ascii=False)


# Esquemas JSON compatibles con OpenAI Function Calling
GET_ORDER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_order",
        "description": "Consulta los detalles de un pedido específico (productos, total, estado, sucursal, fecha) a partir de su ID único.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "El ID único del pedido en formato ORD-XXX (ej. 'ORD-001', 'ORD-002')."
                }
            },
            "required": ["order_id"]
        }
    }
}

LIST_ORDERS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_orders",
        "description": "Lista y filtra múltiples pedidos activos de acuerdo con el estado actual o la sucursal. Permite buscar qué pedidos están en preparación o listar pedidos de sucursales particulares.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["entregado", "en preparación"],
                    "description": "Filtro opcional por estado del pedido."
                },
                "branch": {
                    "type": "string",
                    "description": "Filtro opcional por nombre de la sucursal de origen (ej. 'Roma Norte', 'Condesa', 'Juárez')."
                }
            }
        }
    }
}
