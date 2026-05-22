import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import health, agent, chat

# Configurar el sistema de logging estándar en consola para toda la aplicación
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Café Aurora Agent API",
    description="API REST profesional con agente inteligente y function calling para Café Aurora.",
    version="1.0.0"
)

# Configurar middleware de CORS para habilitar solicitudes seguras
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Registrar enrutadores modulares de la aplicación
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(agent.router)
