import sys
import json
import requests

def iniciar_cliente():
    url = "http://127.0.0.1:8000/agent"
    print("=====================================================================")
    print("        CLIENTE INTERACTIVO - CAFÉ AURORA AGENT API")
    print("=====================================================================")
    print("Escriba su pregunta y presione Enter. Escriba 'salir' para terminar.\n")

    while True:
        try:
            pregunta = input("\nPregunta > ").strip()
            if not pregunta:
                continue
            if pregunta.lower() in ["salir", "exit", "q"]:
                print("Finalizando cliente interactivo.")
                break

            # Envío de la petición POST a la API local
            respuesta = requests.post(url, json={"question": pregunta})

            if respuesta.status_code == 200:
                datos = respuesta.json()
                print("\n--- Respuesta del Agente ---")
                print(datos.get("answer"))
                print("----------------------------")
                
                steps = datos.get("steps", [])
                if steps:
                    print(f"\n[Ruta de razonamiento: {len(steps)} pasos en {datos.get('iterations')} iteraciones | Tiempo: {datos.get('elapsed_seconds'):.3f}s]")
                    for s in steps:
                        print(f"  * Paso {s['iteration']} -> Herramienta: '{s['tool']}' con {s['arguments']}")
                        print(f"    Resultado: {s['result_preview']}")
                else:
                    print(f"\n[Respondido directamente en {datos.get('iterations')} iteraciones | Tiempo: {datos.get('elapsed_seconds'):.3f}s]")
            elif respuesta.status_code == 422:
                print(f"\n[Error 422 - Validación de datos]: La pregunta es demasiado corta (mínimo 3 caracteres).")
            else:
                print(f"\n[Error {respuesta.status_code}]: {respuesta.text}")

        except requests.exceptions.ConnectionError:
            print("\n[Error de Conexión]: No se pudo conectar con el servidor en http://127.0.0.1:8000.")
            print("Asegúrese de tener la API de FastAPI corriendo en otra terminal antes de usar este cliente.")
            break
        except KeyboardInterrupt:
            print("\nFinalizando cliente interactivo.")
            break

if __name__ == "__main__":
    iniciar_cliente()
