import os
import sys
import json
from pathlib import Path
from openai import OpenAI

# Asegurar que el directorio del proyecto esté en el PATH
directorio_base = Path(__file__).resolve().parent
sys.path.append(str(directorio_base))

from config import get_settings
from tools import ALL_TOOLS, TOOL_FUNCTIONS


def main():
    print("--- INICIANDO DEMOSTRACIÓN DE FUNCTION CALLING (FASE 1) ---")

    # Cargar configuraciones
    settings = get_settings()
    
    # Crear cliente de OpenAI
    cliente = OpenAI(api_key=settings.openai_api_key)
    
    # Pregunta de prueba: RAG + Calculadora combinados
    pregunta = "¿Cuánto cuestan 3 lattes de mazapán con el descuento de empleado?"
    print(f"Pregunta del usuario: '{pregunta}'\n")

    # Inicializar historial de mensajes
    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres el asistente oficial de Café Aurora. Responde en castellano natural, neutro y formal. "
                "Cuentas con herramientas para buscar información RAG, realizar cálculos matemáticos y consultar pedidos. "
                "Resuelve paso a paso cuando sea necesario combinando las herramientas."
            ),
        },
        {"role": "user", "content": pregunta}
    ]

    print("Enviando consulta inicial a GPT-4o-mini...")
    
    # Primera llamada al modelo
    respuesta = cliente.chat.completions.create(
        model=settings.model_name,
        messages=mensajes,
        tools=ALL_TOOLS,
        tool_choice="auto",
        temperature=0.0
    )

    mensaje_respuesta = respuesta.choices[0].message
    mensajes.append(mensaje_respuesta)

    # Verificar si el modelo solicitó llamadas a herramientas
    if mensaje_respuesta.tool_calls:
        print(f"El LLM decidió llamar a {len(mensaje_respuesta.tool_calls)} herramienta(s):")
        
        for call in mensaje_respuesta.tool_calls:
            nombre_tool = call.function.name
            try:
                args = json.loads(call.function.arguments)
            except Exception as e:
                print(f"  ERROR: Error decodificando JSON: {e}")
                args = {}
            
            print(f"- Herramienta: {nombre_tool}")
            print(f"  Argumentos: {args}")
            
            # Ejecutar la herramienta correspondiente
            funcion_ejecutable = TOOL_FUNCTIONS.get(nombre_tool)
            if funcion_ejecutable:
                print("  Ejecutando herramienta...")
                # Desempaquetar argumentos de forma segura
                resultado = funcion_ejecutable(**args)
                print(f"  Resultado de la herramienta:\n{resultado}\n")
                
                # Agregar el resultado de la herramienta al historial de mensajes
                mensajes.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": nombre_tool,
                    "content": resultado
                })
            else:
                print(f"  ERROR: Herramienta '{nombre_tool}' no está registrada.")

        print("Enviando resultados de herramientas al LLM para generar respuesta final...")
        
        # Segunda llamada al modelo con los resultados de las herramientas
        segunda_respuesta = cliente.chat.completions.create(
            model=settings.model_name,
            messages=mensajes,
            temperature=0.0
        )
        
        print("Respuesta final del agente:")
        print(segunda_respuesta.choices[0].message.content)
    else:
        print("El LLM respondió directamente sin usar herramientas:")
        print(mensaje_respuesta.content)


if __name__ == "__main__":
    main()
