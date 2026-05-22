import logging
from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_agent_service
from models.agent import AgentRequest, AgentResponse
from services.agent_service import AgentService

# Configurar logger local para el enrutador
logger = logging.getLogger("rag_api.routers.agent")

router = APIRouter()


@router.post(
    "/agent",
    response_model=AgentResponse,
    summary="Consultar al Agente Conversacional Inteligente",
    description=(
        "Envía una pregunta en lenguaje natural al agente de Café Aurora. "
        "El agente resolverá la consulta encadenando de manera autónoma búsquedas RAG "
        "en los documentos del negocio, ejecución de cálculos matemáticos seguros "
        "y consultas a la base de datos de pedidos."
    )
)
def query_agent(
    request: AgentRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Procesa una consulta del usuario y devuelve la respuesta final generada por el agente.

    Este endpoint se ejecuta de forma síncrona (utiliza `def` en lugar de `async def`)
    para garantizar la alineación con los requisitos técnicos del bootcamp. Realiza
    el registro de logs correspondientes y delega la ejecución al AgentService.

    - **request**: Contiene la pregunta ('question') que debe tener mínimo 3 caracteres.
    - **agent_service**: Servicio del agente inyectado automáticamente.
    """
    pregunta = request.question
    logger.info(f"Petición recibida en POST /agent. Pregunta: '{pregunta}'")
    
    try:
        # Ejecutar el bucle principal de razonamiento y herramientas
        respuesta = agent_service.run(pregunta)
        
        logger.info(
            f"Petición resuelta exitosamente. Iteraciones realizadas: {respuesta.iterations}. "
            f"Tiempo total: {respuesta.elapsed_seconds}s."
        )
        return respuesta
        
    except Exception as e:
        logger.error(f"Error procesando la solicitud del agente: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error interno al procesar la solicitud del agente: {str(e)}"
        )
