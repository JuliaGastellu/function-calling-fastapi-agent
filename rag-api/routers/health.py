from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Comprueba el estado operativo general de la API de Café Aurora."
)
def check_health():
    """Devuelve el estado operativo básico de la aplicación."""
    return {
        "status": "ok",
        "app": "Café Aurora Agent API",
        "version": "1.0.0"
    }
