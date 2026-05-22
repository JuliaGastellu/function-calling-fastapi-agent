import time
import json
import logging
from typing import Any
from openai import OpenAI

from config import get_settings
from models.agent import AgentResponse, ToolStep
from tools import ALL_TOOLS, TOOL_FUNCTIONS

logger = logging.getLogger("rag_api.services.agent_service")

# Prompt del sistema estructurado para regir el comportamiento del agente
SYSTEM_PROMPT = """Eres el asistente virtual oficial de Café Aurora, un sistema de asistencia inteligente profesional para clientes y personal de la cafetería.
Responde de manera concisa, clara, directa y en castellano natural, fluido y correcto.
No utilices emojis de ningún tipo ni expreses emocionalidad o entusiasmo exagerado en tus respuestas. Mantén un tono formal, profesional y neutro en todo momento.

Cuentas con las siguientes herramientas específicas que debes utilizar obligatoriamente para resolver las consultas del usuario:
1. 'search_documents': para buscar información en el RAG (menú, precios de bebidas y alimentos, historia de la cafetería, fundadores y políticas de empleados).
2. 'calculate': para evaluar de manera exacta expresiones aritméticas sencillas.
3. 'get_order': para consultar los detalles de un pedido específico mediante su ID único en formato 'ORD-XXX'.
4. 'list_orders': para listar y filtrar pedidos según su estado o sucursal de origen.
5. 'get_hours': para consultar la dirección, contacto y horarios semanales detallados de una sucursal específica.

Directrices estrictas de resolución de problemas:
- Sé proactivo: Si una consulta requiere información interna que no está provista en el mensaje del usuario, búscala primero en tus documentos usando 'search_documents' (ej. políticas de descuento de empleados, precios de bebidas, fundadores, vacaciones, etc.).
- No asumas datos ni le preguntes al usuario por información si puedes obtenerla buscando en tus documentos o llamando a herramientas.
- Si requieres hacer cálculos de dinero o cantidades (como descuentos de empleado, impuestos como el 16% de IVA, sumas, multiplicaciones, promedios), SIEMPRE debes utilizar la herramienta 'calculate' con los datos numéricos exactos recuperados. No intentes realizar cálculos aritméticos en el texto directamente.
- Sigue un proceso secuencial y encadena las herramientas cuando sea necesario. Por ejemplo:
  1. Llama a 'search_documents' o 'get_order' para obtener la información o precios.
  2. Llama a 'calculate' para aplicar el descuento, el IVA, el promedio o la multiplicación.
  3. Formula la respuesta formal final con los datos exactos.
- Si la información sobre una consulta no está disponible en las herramientas o los documentos tras haberlos buscado activamente, dilo de forma clara y profesional sin inventar datos.
- Si el usuario te saluda de forma general o realiza una consulta trivial que no requiere herramientas, responde directamente en castellano natural y con el tono formal correspondiente, sin llamar a herramientas y manteniendo la lista de pasos 'steps' vacía.
"""


class AgentService:
    """Clase de servicio encargada de gestionar el bucle de ejecución y llamadas a OpenAI y herramientas."""

    def __init__(self) -> None:
        """Inicializa el cliente de OpenAI y carga la configuración centralizada."""
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.model_name
        self.max_iterations = settings.max_iterations

    def run(self, question: str) -> AgentResponse:
        """Ejecuta el bucle del agente (agent loop) para resolver la pregunta del usuario.

        Args:
            question (str): Pregunta planteada por el usuario.

        Returns:
            AgentResponse: Objeto conteniendo la respuesta estructurada, pasos seguidos e iteraciones.
        """
        logger.info(f"Iniciando ejecución del agente. Pregunta recibida: '{question}'")
        tiempo_inicio_global = time.time()

        # Inicializar historial de conversación del modelo
        historial_mensajes = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        pasos: list[ToolStep] = []
        contador_iteraciones = 0

        while contador_iteraciones < self.max_iterations:
            contador_iteraciones += 1
            logger.info(f"Ejecutando iteración {contador_iteraciones} de {self.max_iterations}...")

            try:
                # Llamar al modelo OpenAI GPT-4o-mini
                respuesta_llm = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=historial_mensajes,
                    tools=ALL_TOOLS,
                    tool_choice="auto",
                    temperature=0.0
                )
            except Exception as e:
                logger.error(f"Error al llamar al SDK de OpenAI: {e}")
                raise RuntimeError(f"Error de conexión con OpenAI: {str(e)}")

            choice = respuesta_llm.choices[0]
            mensaje = choice.message

            # Registrar la respuesta del modelo en el historial de la conversación
            historial_mensajes.append(mensaje)

            # Verificar si el modelo solicitó llamadas a herramientas
            if mensaje.tool_calls:
                logger.info(f"El LLM solicitó {len(mensaje.tool_calls)} llamadas a herramientas en iteración {contador_iteraciones}.")

                # Ejecutar cada llamada a herramienta secuencialmente
                for call in mensaje.tool_calls:
                    nombre_tool = call.function.name
                    args_str = call.function.arguments

                    logger.info(f"Llamando a herramienta '{nombre_tool}' con argumentos: {args_str}")
                    tiempo_inicio_tool = time.time()

                    try:
                        args = json.loads(args_str)
                    except Exception as e:
                        logger.error(f"Error decodificando argumentos JSON para '{nombre_tool}': {e}")
                        args = {}

                    # Ejecutar la herramienta correspondiente
                    funcion_ejecutable = TOOL_FUNCTIONS.get(nombre_tool)
                    if funcion_ejecutable:
                        try:
                            resultado_tool = funcion_ejecutable(**args)
                        except Exception as err:
                            resultado_tool = f"Error en ejecución de herramienta: {str(err)}"
                    else:
                        resultado_tool = f"Error: La herramienta '{nombre_tool}' no está registrada en el sistema."

                    tiempo_fin_tool = time.time()
                    duracion_tool = tiempo_fin_tool - tiempo_inicio_tool
                    logger.info(f"Herramienta '{nombre_tool}' completada en {duracion_tool:.4f} segundos.")

                    # Generar vista previa del resultado para no saturar el log de pasos
                    vista_previa = resultado_tool
                    if len(vista_previa) > 500:
                        vista_previa = vista_previa[:497] + "..."

                    # Registrar el paso de herramienta ejecutado
                    pasos.append(
                        ToolStep(
                            iteration=contador_iteraciones,
                            tool=nombre_tool,
                            arguments=args,
                            result_preview=vista_previa,
                            elapsed_seconds=round(duracion_tool, 4)
                        )
                    )

                    # Añadir el resultado de la herramienta en el historial para la siguiente iteración
                    historial_mensajes.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": nombre_tool,
                        "content": resultado_tool
                    })
            else:
                # El modelo no solicita más herramientas y entrega la respuesta en lenguaje natural
                logger.info("El LLM completó el ciclo y generó la respuesta final.")
                tiempo_total = time.time() - tiempo_inicio_global
                return AgentResponse(
                    answer=mensaje.content or "",
                    steps=pasos,
                    iterations=contador_iteraciones,
                    elapsed_seconds=round(tiempo_total, 4)
                )

        # Si el bucle excede el máximo de iteraciones como red de seguridad (safety net)
        logger.warning(f"Bucle del agente superó el límite de {self.max_iterations} iteraciones.")
        tiempo_total = time.time() - tiempo_inicio_global
        
        # Solicitar respuesta final rápida
        historial_mensajes.append({
            "role": "user",
            "content": "Por favor, elabora tu respuesta final con los datos que posees en este momento."
        })
        try:
            respuesta_emergencia = self.client.chat.completions.create(
                model=self.model_name,
                messages=historial_mensajes,
                temperature=0.0
            )
            respuesta_final = respuesta_emergencia.choices[0].message.content or ""
        except Exception:
            respuesta_final = "No fue posible finalizar el ciclo del agente de forma exitosa dentro del límite de iteraciones."

        return AgentResponse(
            answer=respuesta_final,
            steps=pasos,
            iterations=contador_iteraciones,
            elapsed_seconds=round(tiempo_total, 4)
        )
