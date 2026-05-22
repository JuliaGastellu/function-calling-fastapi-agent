# Entrega de la Semana 10: Café Aurora Agent API

Este proyecto de nivel profesional constituye la entrega académica correspondiente a la **Semana 10 del Bootcamp de AI Engineering**. Consiste en una API REST construida sobre FastAPI y el SDK de OpenAI, la cual da soporte a un agente conversacional inteligente equipado con capacidades nativas de llamada a funciones (*function calling*).

El agente es capaz de resolver consultas complejas encadenando herramientas de forma secuencial y autónoma: busca en documentos de conocimiento del negocio mediante recuperación semántica (RAG), realiza cálculos matemáticos con absoluta precisión y seguridad, y consulta información sobre el estado y origen de los pedidos de la cafetería.

---

## Características Principales

1. **Llamada a Funciones Nativa (*Function Calling*)**: Implementada a través del SDK oficial de OpenAI y potenciada por el modelo de última generación `gpt-4o-mini` con temperatura `0.0` para garantizar un comportamiento determinista.
2. **Arquitectura del Bucle del Agente (*Agent Loop*)**: Implementada en la capa de servicios (`AgentService.run`). Realiza múltiples iteraciones para encadenar llamadas a herramientas cuando una consulta compleja lo requiere, contando con una red de seguridad (*safety net*) de máximo 5 iteraciones.
3. **Calculadora Segura**: Un evaluador matemático desarrollado a nivel sintáctico mediante el módulo estándar `ast` de Python. Analiza y ejecuta expresiones aritméticas básicas (como sumas, porcentajes de impuestos, multiplicaciones de precios) y rechaza cualquier nodo sintáctico inseguro, evitando por completo el uso de la función peligrosa `eval()`.
4. **Buscador RAG sobre ChromaDB**: Utiliza recuperación semántica en disco sobre una colección de ChromaDB poblada con documentos enriquecidos (menú de alimentos y bebidas, historia del negocio y políticas de empleados). Implementa inicialización diferida (*lazy initialization*) para mejorar los tiempos de arranque de la API.
5. **Consulta de Pedidos**: Capacidad de recuperar detalles de pedidos individuales o filtrar listas de órdenes según el estado y la sucursal de origen.
6. **Bono Creativo (5ta Herramienta)**: Incorpora un sistema de consulta de horarios de atención semanales y contacto detallado para cada una de las sucursales oficiales de Café Aurora ("Roma Norte", "Condesa" y "Juárez").
7. **Suite de Pruebas Automatizadas**: Script autónomo que evalúa y valida 14 casos de prueba distintos, desde consultas puras de RAG y cálculos complejos hasta encadenamientos multi-herramienta y manejo de casos extremos y validaciones.

---

## Estructura de Archivos del Proyecto

La estructura profesional del proyecto modular de FastAPI está organizada bajo el directorio raíz `rag-api/`:

```
rag-api/
├── .env                           # Credenciales y variables de configuración (OPENAI_API_KEY)
├── requirements.txt               # Declaración de dependencias del sistema
├── config.py                      # Clase de configuración centralizada con Pydantic-Settings
├── dependencies.py                # Proveedores y dependencias de inyección de FastAPI (get_agent_service)
├── main.py                        # Punto de entrada de FastAPI y registro de enrutadores
├── db_initializer.py              # Script para inicializar y poblar ChromaDB con embeddings vectoriales
├── demo_function_calling.py       # Demostración independiente en consola de la Fase 1
├── run_tests.py                   # Suite de pruebas automatizadas completa
├── chroma_db_advanced/            # Carpeta persistente con la base de datos vectorial ChromaDB
├── models/
│   ├── __init__.py
│   └── agent.py                   # Modelos de datos Pydantic (AgentRequest, ToolStep, AgentResponse)
├── routers/
│   ├── __init__.py
│   ├── health.py                  # Endpoint GET / para diagnóstico de salud del servicio
│   └── agent.py                   # Endpoint POST /agent para interactuar síncronamente con el agente
├── services/
│   ├── __init__.py
│   └── agent_service.py           # Bucle principal de razonamiento e integración del agente (AgentService)
└── tools/
    ├── __init__.py
    ├── calculator_tool.py         # Calculadora aritmética segura con ast.parse (no eval)
    ├── rag_tool.py                # Búsqueda semántica lazy-initialized en la base de datos ChromaDB
    ├── orders_tool.py             # Consulta y listado de pedidos simulados en memoria
    └── hours_tool.py              # Bono: Consulta de horarios y contacto por sucursal
```

---

## Configuración y Despliegue

### 1. Requisitos Previos

Asegúrese de contar con Python 3.10 o superior y las dependencias instaladas:

```bash
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno

Cree un archivo `.env` en la raíz de la carpeta `rag-api/` con la siguiente estructura:

```env
OPENAI_API_KEY=su_clave_api_de_openai
MODEL_NAME=gpt-4o-mini
CHROMA_DB_PATH=chroma_db_advanced
MAX_ITERATIONS=5
```

### 3. Inicialización del Almacén de Vectores (ChromaDB)

Antes de iniciar la API por primera vez, ejecute el inicializador de la base de datos. Este script creará la colección RAG e indexará las políticas, menús e historia oficiales con embeddings del modelo oficial de OpenAI `text-embedding-3-small`:

```bash
python db_initializer.py
```

### 4. Ejecución del Servidor de Desarrollo

Inicie el servidor web de FastAPI mediante uvicorn:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

El servidor estará operativo en `http://localhost:8000/`. Puede acceder a la documentación interactiva Swagger directamente a través de:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Ejecución de Pruebas Automatizadas

El proyecto incluye una suite de pruebas que valida 14 casos que cubren de manera exhaustiva el funcionamiento del agente conversacional.

Para ejecutar las pruebas de manera 100% autónoma, simplemente ejecute:

```bash
python run_tests.py
```

El script verificará de forma híbrida: si el servidor FastAPI en el puerto 8000 está activo, realizará peticiones reales por red utilizando `requests`; si no se detecta el servidor, instanciará de forma transparente el cliente de pruebas `TestClient` de FastAPI para ejecutar y validar los casos de forma local y ultrarrápida.

### Casos de Prueba Incluidos

1. **RAG Puro (Búsqueda en documentos)**:
   - Consulta de precio del latte de mazapán (esperado: $72).
   - Consulta sobre los fundadores de la cafetería y fecha de fundación (esperado: Aurora Reyes y Carlos Gómez en 2018).
   - Consulta sobre días de vacaciones en el primer año (esperado: 12 días).
2. **Calculadora Pura (Cálculos directos)**:
   - Operación matemática simple `72 * 5` (esperado: 360).
   - Cálculo de 16% de IVA sobre un total de $350 (esperado: 56).
3. **Pedidos Puros (Consulta simulada)**:
   - Consulta sobre el estado del pedido específico `ORD-001` (esperado: entregado).
   - Consulta sobre qué pedidos están en preparación (esperado: ORD-002 y ORD-003).
   - Consulta sobre pedidos en la sucursal de Roma Norte (esperado: ORD-001 y ORD-002).
4. **Encadenamiento Multi-herramienta (Multi-tool Chaining)**:
   - *RAG + Calculadora*: Precio de 3 lattes de mazapán con descuento de empleado (10%). El agente buscará el precio y la política, y ejecutará `calculate("72 * 3 * 0.9")` (esperado: $194.40).
   - *Pedidos + Calculadora*: Total de pedido `ORD-002` aplicando el 16% de IVA. El agente recuperará el total del pedido ($165) y ejecutará `calculate("165 * 1.16")` (esperado: $191.40).
   - *RAG + Calculadora*: Cálculo del promedio de precios de las bebidas calientes en base a los datos del menú.
5. **Casos de Frontera (Edge Cases)**:
   - Consulta trivial sin herramientas (ej. "Hola, ¿cómo estás?") (esperado: respuesta directa, sin pasos).
   - Consulta de pedido inexistente `ORD-999` (esperado: respuesta elegante de "Pedido no encontrado").
   - Validación robusta de Pydantic para preguntas de menos de 3 caracteres (ej. "ab") (esperado: código HTTP 422).
