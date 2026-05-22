import sys
import json
import requests
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en el PATH
directorio_base = Path(__file__).resolve().parent
sys.path.append(str(directorio_base))

from main import app
from fastapi.testclient import TestClient

# Casos de prueba a evaluar con sus validaciones esperadas
CASOS_DE_PRUEBA = [
    {
        "nombre": "1. RAG - Precio de Latte de Mazapán",
        "question": "¿Cuánto cuesta el latte de mazapán?",
        "validar": lambda res: "72" in res.get("answer", "") and any(s["tool"] == "search_documents" for s in res.get("steps", []))
    },
    {
        "nombre": "2. RAG - Fundadores e Historia",
        "question": "¿Quién fundó Café Aurora y cuándo?",
        "validar": lambda res: ("aurora reyes" in res.get("answer", "").lower() or "carlos gómez" in res.get("answer", "").lower()) and "2018" in res.get("answer", "")
    },
    {
        "nombre": "3. RAG - Vacaciones de Empleados",
        "question": "¿Cuántos días de vacaciones tengo el primer año?",
        "validar": lambda res: "12" in res.get("answer", "") and any(s["tool"] == "search_documents" for s in res.get("steps", []))
    },
    {
        "nombre": "4. Calculadora - Cálculo Directo",
        "question": "¿Cuánto es 72 * 5?",
        "validar": lambda res: "360" in res.get("answer", "") and any(s["tool"] == "calculate" for s in res.get("steps", []))
    },
    {
        "nombre": "5. Calculadora - IVA 16% sobre $350",
        "question": "¿Cuánto es el 16% de IVA sobre $350?",
        "validar": lambda res: "56" in res.get("answer", "") and any(s["tool"] == "calculate" for s in res.get("steps", []))
    },
    {
        "nombre": "6. Pedido Específico - Estado ORD-001",
        "question": "¿Cuál es el estado del pedido ORD-001?",
        "validar": lambda res: "entregado" in res.get("answer", "").lower() and any(s["tool"] == "get_order" for s in res.get("steps", []))
    },
    {
        "nombre": "7. Pedidos - Listar por Estado",
        "question": "¿Qué pedidos están en preparación?",
        "validar": lambda res: "ord-002" in res.get("answer", "").lower() and "ord-003" in res.get("answer", "").lower()
    },
    {
        "nombre": "8. Pedidos - Listar por Sucursal",
        "question": "¿Cuáles son los pedidos de Roma Norte?",
        "validar": lambda res: "ord-001" in res.get("answer", "").lower() and "ord-002" in res.get("answer", "").lower()
    },
    {
        "nombre": "9. Multi-tool - RAG + Calculadora (Mazapán Descuento)",
        "question": "¿Cuánto cuestan 3 lattes de mazapán con el descuento de empleado?",
        "validar": lambda res: "194.4" in res.get("answer", "") and len(res.get("steps", [])) >= 2
    },
    {
        "nombre": "10. Multi-tool - Pedidos + Calculadora (ORD-002 con IVA)",
        "question": "¿Cuánto sale el pedido ORD-002 con 16% de IVA?",
        "validar": lambda res: "191.4" in res.get("answer", "") and len(res.get("steps", [])) >= 2
    },
    {
        "nombre": "11. Multi-tool - RAG + Calculadora (Promedio Bebidas Calientes)",
        "question": "¿Cuál es el precio promedio de las bebidas calientes?",
        "validar": lambda res: len(res.get("steps", [])) >= 2
    },
    {
        "nombre": "12. Edge Case - Sin Herramientas (Conversación Directa)",
        "question": "Hola, ¿cómo estás?",
        "validar": lambda res: len(res.get("steps", [])) == 0 and len(res.get("answer", "")) > 0
    },
    {
        "nombre": "13. Edge Case - Pedido Inexistente",
        "question": "¿Estado del pedido ORD-999?",
        "validar": lambda res: any(x in res.get("answer", "").lower() for x in ["no encontrado", "no se encuentra", "inexistente", "no registrado"])
    },
    {
        "nombre": "14. Edge Case - Validación Pydantic (Pregunta Corta)",
        "question": "ab",
        "validar": None  # Esperamos un código de estado HTTP 422
    }
]


def ejecutar_pruebas():
    print("--- INICIANDO VERIFICACIÓN DE SUITE DE PRUEBAS AUTOMATIZADAS ---")
    
    # Determinar si el servidor real está arriba en el puerto 8000
    usar_test_client = False
    api_url = "http://localhost:8000/agent"
    
    try:
        resp_health = requests.get("http://localhost:8000/", timeout=2)
        if resp_health.status_code == 200:
            print("Servidor operativo en puerto 8000. Ejecutando mediante peticiones HTTP...")
        else:
            usar_test_client = True
    except Exception:
        usar_test_client = True

    if usar_test_client:
        print("Servidor local no detectado. Iniciando TestClient autónomo para las pruebas...")
        cliente = TestClient(app)
    else:
        cliente = None

    exitosas = 0
    fallidas = 0

    for caso in CASOS_DE_PRUEBA:
        nombre = caso["nombre"]
        pregunta = caso["question"]
        validador = caso["validar"]

        print(f"\nEjecutando: {nombre}")
        print(f"Pregunta: '{pregunta}'")

        if validador is None:
            # Caso 14: Esperamos fallo de validación Pydantic (422)
            if cliente:
                res = cliente.post("/agent", json={"question": pregunta})
            else:
                res = requests.post(api_url, json={"question": pregunta})
            
            if res.status_code == 422:
                print("-> [PASADO] Recibido código 422 de error de validación esperado.")
                exitosas += 1
            else:
                print(f"-> [FALLADO] Se esperaba código 422, pero se recibió {res.status_code}.")
                fallidas += 1
        else:
            # Casos normales
            if cliente:
                res = cliente.post("/agent", json={"question": pregunta})
            else:
                res = requests.post(api_url, json={"question": pregunta})

            if res.status_code == 200:
                datos = res.json()
                print(f"Respuesta del agente: {datos.get('answer')}")
                print(f"Pasos realizados: {len(datos.get('steps', []))} | Iteraciones: {datos.get('iterations')} | Tiempo: {datos.get('elapsed_seconds')}s")
                for s in datos.get("steps", []):
                    print(f"  * Iteración {s['iteration']} -> Herramienta: {s['tool']} | Args: {s['arguments']}")
                
                # Evaluar el validador personalizado
                if validador(datos):
                    print("-> [PASADO] La respuesta cumple con los criterios de validación.")
                    exitosas += 1
                else:
                    print("-> [FALLADO] La respuesta no contiene los valores o herramientas esperados.")
                    print("JSON recibido:", json.dumps(datos, ensure_ascii=False, indent=2))
                    fallidas += 1
            else:
                print(f"-> [FALLADO] La llamada falló con código HTTP {res.status_code}.")
                print(res.text)
                fallidas += 1

    print("\n--- RESUMEN DE PRUEBAS ---")
    print(f"Total Evaluadas: {len(CASOS_DE_PRUEBA)}")
    print(f"Exitosas       : {exitosas}")
    print(f"Fallidas       : {fallidas}")
    
    if fallidas == 0:
        print("\nTodas las pruebas han pasado satisfactoriamente. API 100% operativa.")
        sys.exit(0)
    else:
        print(f"\nSe detectaron {fallidas} fallos en las pruebas.")
        sys.exit(1)


if __name__ == "__main__":
    ejecutar_pruebas()
