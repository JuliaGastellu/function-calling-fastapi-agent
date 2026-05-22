from functools import lru_cache
from services.agent_service import AgentService


@lru_cache
def get_agent_service() -> AgentService:
    """Devuelve e inyecta una instancia única singleton de AgentService."""
    return AgentService()
