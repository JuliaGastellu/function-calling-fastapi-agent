from typing import Any
from pydantic import BaseModel, Field, field_validator


class AgentRequest(BaseModel):
    """Modelo de solicitud que recibe la pregunta del usuario."""

    question: str = Field(
        ...,
        description="Pregunta del usuario para el agente conversacional."
    )

    @field_validator("question")
    @classmethod
    def validar_pregunta(cls, v: str) -> str:
        """Asegura que la pregunta tenga al menos 3 caracteres tras limpiar espacios."""
        limpia = v.strip()
        if len(limpia) < 3:
            raise ValueError("String should have at least 3 characters")
        return limpia


class ToolStep(BaseModel):
    """Modelo que representa una iteración de ejecución de herramienta."""

    iteration: int = Field(..., description="Número de iteración actual.")
    tool: str = Field(..., description="Nombre de la herramienta ejecutada.")
    arguments: dict[str, Any] = Field(..., description="Argumentos de entrada provistos por el LLM.")
    result_preview: str = Field(..., description="Vista previa en texto del resultado de la herramienta.")
    elapsed_seconds: float = Field(..., description="Tiempo total empleado en la ejecución de la herramienta.")


class AgentResponse(BaseModel):
    """Modelo que estructurará la respuesta final entregada por el agente."""

    answer: str = Field(..., description="Respuesta estructurada en lenguaje natural del agente.")
    steps: list[ToolStep] = Field(default_factory=list, description="Historial secuencial de herramientas ejecutadas.")
    iterations: int = Field(..., description="Total de iteraciones realizadas en el bucle del agente.")
    elapsed_seconds: float = Field(..., description="Tiempo total transcurrido desde el inicio de la solicitud.")
