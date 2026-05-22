import json
from typing import Optional

# Base de datos simulada de horarios por sucursal
HORARIOS_SUCURSALES = {
    "roma norte": {
        "sucursal": "Roma Norte",
        "direccion": "Calle Colima 123, Roma Norte, CDMX",
        "horario_semanal": "Lunes a Sábado de 07:00 a 22:00",
        "domingos": "Cerrado",
        "contacto": "roma@cafeaurora.com | +52 55 1234 5678"
    },
    "condesa": {
        "sucursal": "Condesa",
        "direccion": "Avenida Amsterdam 45, Hipódromo Condesa, CDMX",
        "horario_semanal": "Lunes a Sábado de 08:00 a 21:00",
        "domingos": "Cerrado",
        "contacto": "condesa@cafeaurora.com | +52 55 8765 4321"
    },
    "juárez": {
        "sucursal": "Juárez",
        "direccion": "Calle Havre 89, Juárez, CDMX",
        "horario_semanal": "Lunes a Sábado de 07:30 a 21:30",
        "domingos": "Cerrado",
        "contacto": "juarez@cafeaurora.com | +52 55 5678 1234"
    }
}


def get_hours(branch: str) -> str:
    """Consulta la dirección, horarios de apertura semanales y contacto de una sucursal de Café Aurora.

    Args:
        branch (str): Nombre de la sucursal a consultar (ej. 'Roma Norte', 'Condesa', 'Juárez').

    Returns:
        str: Representación en JSON con los horarios e información o mensaje de error.
    """
    clave = branch.strip().lower()
    info = HORARIOS_SUCURSALES.get(clave)
    
    # Intento de coincidencia parcial si la clave exacta falla
    if not info:
        for k, v in HORARIOS_SUCURSALES.items():
            if k in clave or clave in k:
                info = v
                break

    if not info:
        return f"Sucursal '{branch}' no encontrada. Sucursales disponibles: Roma Norte, Condesa, Juárez."

    return json.dumps(info, ensure_ascii=False)


# Esquema JSON compatible con OpenAI Function Calling
HOURS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_hours",
        "description": "Consulta los horarios semanales de atención, dirección y contacto de una sucursal específica de Café Aurora.",
        "parameters": {
            "type": "object",
            "properties": {
                "branch": {
                    "type": "string",
                    "description": "Nombre de la sucursal de la cual obtener horarios y datos (ej. 'Roma Norte', 'Condesa', 'Juárez')."
                }
            },
            "required": ["branch"]
        }
    }
}
