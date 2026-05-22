import ast
import operator
from typing import Union

# Mapeo de operadores binarios permitidos de forma segura
OPERADORES_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

# Mapeo de operadores unarios permitidos (ej. valores negativos)
OPERADORES_UNARIOS = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluar_nodo(nodo: ast.AST) -> Union[int, float]:
    """Evalúa recursivamente un nodo de árbol de sintaxis abstracta (AST)."""
    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, (int, float)):
            return nodo.value
        raise ValueError("Se detectó un valor no numérico en la expresión.")

    elif isinstance(nodo, ast.BinOp):
        tipo_op = type(nodo.op)
        if tipo_op not in OPERADORES_BINARIOS:
            raise ValueError(f"Operador binario '{tipo_op.__name__}' no permitido.")
        izq = _evaluar_nodo(nodo.left)
        der = _evaluar_nodo(nodo.right)
        return OPERADORES_BINARIOS[tipo_op](izq, der)

    elif isinstance(nodo, ast.UnaryOp):
        tipo_op = type(nodo.op)
        if tipo_op not in OPERADORES_UNARIOS:
            raise ValueError(f"Operador unario '{tipo_op.__name__}' no permitido.")
        operando = _evaluar_nodo(nodo.operand)
        return OPERADORES_UNARIOS[tipo_op](operando)

    elif isinstance(nodo, ast.Expression):
        return _evaluar_nodo(nodo.body)

    else:
        raise ValueError(f"Sintaxis o nodo '{type(nodo).__name__}' no permitido.")


def calculate(expression: str) -> str:
    """Evalúa de forma segura una expresión matemática pasada en texto y devuelve el resultado en texto.

    Args:
        expression (str): Expresión matemática a evaluar (ej. '72 * 3 * 0.9').

    Returns:
        str: Resultado de la operación o mensaje de error.
    """
    try:
        # Reemplazar posibles caracteres de formato que representen moneda
        limpia = expression.replace("$", "").replace("MXN", "").strip()
        # Analizar sintácticamente la expresión
        arbol = ast.parse(limpia, mode="eval")
        resultado = _evaluar_nodo(arbol)
        return str(resultado)
    except Exception as e:
        return f"Error al evaluar la expresión: {str(e)}"


# Esquema JSON compatible con OpenAI Function Calling
CALCULATOR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evalúa expresiones matemáticas sencillas de forma exacta. Úsala cuando necesites calcular precios, descuentos, impuestos o promedios basados en números recuperados.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "La expresión matemática aritmética a resolver (ej. '72 * 3 * 0.9' o '350 * 0.16')."
                }
            },
            "required": ["expression"]
        }
    }
}
