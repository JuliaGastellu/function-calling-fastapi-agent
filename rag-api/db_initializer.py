import os
import sys
from pathlib import Path
import chromadb
from openai import OpenAI

# Asegurar que el directorio raíz del proyecto esté en el PATH
directorio_base = Path(__file__).resolve().parent
sys.path.append(str(directorio_base))

# Intentar cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv(directorio_base / ".env")
except ImportError:
    pass

# Documentos estructurados y enriquecidos de Café Aurora
DOCUMENTOS_CONOCIMIENTO = [
    {
        "id": "doc:historia:sem:0001",
        "texto": (
            "Historia y propuesta de valor de Café Aurora: Café Aurora es una cafetería de barrio enfocada "
            "en café de especialidad y repostería artesanal de alta calidad. Fue fundada en el año 2018 por "
            "la barista Aurora Reyes y el maestro tostador Carlos Gómez. Nació con una idea simple y clara: "
            "ofrecer bebidas consistentes de alta gama, brindar un trato cálido y cercano a la comunidad, y "
            "proporcionar un espacio cómodo, tranquilo y bien iluminado para que las personas puedan leer, "
            "trabajar de forma remota o conversar plácidamente."
        ),
        "metadata": {
            "doc_id": "doc:historia",
            "titulo": "Historia y propuesta de valor de Café Aurora",
            "fuente": "docs/historia.md",
            "chunking": "semantico"
        }
    },
    {
        "id": "doc:menu:sem:0001",
        "texto": (
            "Menú base de Café Aurora - Cafés y Bebidas: Este menú es orientativo y puede variar ligeramente "
            "según la temporada del año. Para opciones sin lactosa, la mayoría de las bebidas se pueden preparar "
            "con bebida vegetal (avena o soja) por solicitud. Los precios vigentes son:\n"
            "- Espresso: corto, intenso y aromático. Precio: $35 MXN.\n"
            "- Americano: espresso alargado con agua caliente purificada. Precio: $40 MXN.\n"
            "- Latte: espresso premium con leche finamente texturizada y sedosa. Precio: $50 MXN.\n"
            "- Cappuccino: espresso balanceado con leche caliente y espuma densa y cremosa. Precio: $48 MXN.\n"
            "- Latte de mazapán: deliciosa bebida especialidad de espresso con leche texturizada y sabor dulce tradicional "
            "del mazapán. Precio: $72 MXN.\n"
            "- Cold brew: café de especialidad extraído en frío lentamente por 12 horas, suave y con baja acidez percibida. "
            "Precio: $60 MXN."
        ),
        "metadata": {
            "doc_id": "doc:menu",
            "titulo": "Menú base de Café Aurora",
            "fuente": "docs/menu.md",
            "chunking": "semantico"
        }
    },
    {
        "id": "doc:menu:sem:0002",
        "texto": (
            "Menú base de Café Aurora - Alimentos y Repostería:\n"
            "- Croissant de mantequilla: repostería horneada diariamente con mantequilla pura. Precio: $40 MXN.\n"
            "- Bizcocho de limón: glaseado clásico con ralladura fresca de limón. Precio: $45 MXN.\n"
            "- Brownie de chocolate: de consistencia densa y húmeda con trozos de nuez. Precio: $50 MXN.\n"
            "- Tostada de aguacate con tomate: pan artesanal de masa madre con aguacate y tomate cherry. Precio: $85 MXN.\n"
            "- Sándwich de pollo y mostaza suave: pan chapata con pechuga de pollo, lechuga y mostaza. Precio: $125 MXN.\n"
            "- Bocadillo vegetariano con hummus y verduras asadas: berenjena, calabacín y hummus casero. Precio: $110 MXN."
        ),
        "metadata": {
            "doc_id": "doc:menu",
            "titulo": "Menú base de Café Aurora - Repostería y Salados",
            "fuente": "docs/menu.md",
            "chunking": "semantico"
        }
    },
    {
        "id": "doc:politicas:sem:0001",
        "texto": (
            "Políticas de atención, horarios y pagos en Café Aurora:\n"
            "- Horarios: Café Aurora abre sus puertas de Lunes a Sábado de 07:00 a 22:00. Los domingos permanece cerrado "
            "durante todo el día para descanso del equipo.\n"
            "- Pagos: Se aceptan pagos en efectivo y con tarjetas de débito o crédito bancarias. Para facturación fiscal, "
            "solicite su ticket y proporcione sus datos fiscales al personal antes de que se proceda a cerrar el pago en caja.\n"
            "- Cambios y devoluciones: Si una bebida no cumple con sus expectativas de temperatura o intensidad, el personal "
            "está plenamente autorizado a ajustarla o rehacerla de forma inmediata y amable."
        ),
        "metadata": {
            "doc_id": "doc:politicas",
            "titulo": "Políticas de atención y horarios en Café Aurora",
            "fuente": "docs/politicas.md",
            "chunking": "semantico"
        }
    },
    {
        "id": "doc:politicas:sem:0002",
        "texto": (
            "Políticas de Recursos Humanos y Beneficios de Empleados en Café Aurora:\n"
            "- Vacaciones: Los empleados contratados de Café Aurora gozan de excelentes condiciones laborales. "
            "Durante el primer año de servicio continuo, los trabajadores tienen derecho por política a disfrutar "
            "de exactamente 12 días de vacaciones pagadas anuales para su libre recreación y descanso.\n"
            "- Descuento de empleado: Todos los empleados de Café Aurora cuentan con un beneficio exclusivo consistente "
            "en un descuento de empleado del 10% (lo que equivale a aplicar un factor de 0.90) en cualquier compra o consumo "
            "personal de bebidas o alimentos que realicen dentro de la cafetería."
        ),
        "metadata": {
            "doc_id": "doc:politicas",
            "titulo": "Políticas y Beneficios para Empleados en Café Aurora",
            "fuente": "docs/politicas.md",
            "chunking": "semantico"
        }
    }
]


def inicializar_base_de_datos() -> None:
    """Inicializa la base de datos vectorial Chroma, genera embeddings e indexa los documentos."""
    print("--- INICIANDO INICIALIZACIÓN DE CHROMA DB ---")
    
    # Obtener API Key de OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: La variable de entorno OPENAI_API_KEY no está definida.")
        print("Por favor, configúrala en el sistema o crea un archivo .env en 'rag-api/'.")
        sys.exit(1)

    # Definir la ruta de la base de datos ChromaDB
    ruta_db = directorio_base / "chroma_db_advanced"
    print(f"Ruta de base de datos: {ruta_db}")

    # Inicializar el cliente persistente de Chroma
    cliente_chroma = chromadb.PersistentClient(path=str(ruta_db))
    
    # Crear o recrear la colección
    nombre_coleccion = "cafe_aurora_semantico"
    try:
        # Eliminar si ya existe para asegurar una carga limpia
        cliente_chroma.delete_collection(name=nombre_coleccion)
        print(f"Colección previa '{nombre_coleccion}' eliminada.")
    except Exception:
        pass
        
    coleccion = cliente_chroma.create_collection(
        name=nombre_coleccion,
        metadata={"hnsw:space": "l2"}
    )
    print(f"Nueva colección '{nombre_coleccion}' creada con éxito.")

    # Inicializar cliente de OpenAI
    cliente_openai = OpenAI(api_key=api_key)

    # Indexar documentos
    print(f"Generando embeddings e indexando {len(DOCUMENTOS_CONOCIMIENTO)} fragmentos...")
    
    ids = []
    textos = []
    metadatos = []
    
    for doc in DOCUMENTOS_CONOCIMIENTO:
        ids.append(doc["id"])
        textos.append(doc["texto"])
        metadatos.append(doc["metadata"])

    try:
        # Generar embeddings de todos los fragmentos
        respuesta_emb = cliente_openai.embeddings.create(
            model="text-embedding-3-small",
            input=textos
        )
        vectores = [item.embedding for item in respuesta_emb.data]
        
        # Insertar datos en ChromaDB
        coleccion.add(
            ids=ids,
            documents=textos,
            metadatas=metadatos,
            embeddings=vectores
        )
        print("--- INDEXACIÓN COMPLETADA CON ÉXITO ---")
        print(f"Total de registros cargados: {coleccion.count()}")
        
    except Exception as e:
        print(f"ERROR DURANTE LA GENERACIÓN DE EMBEDDINGS/INDEXACIÓN: {e}")
        sys.exit(1)


if __name__ == "__main__":
    inicializar_base_de_datos()
