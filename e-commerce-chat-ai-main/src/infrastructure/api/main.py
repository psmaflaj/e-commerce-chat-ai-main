"""
Aplicación FastAPI con endpoints:
- GET /, /health
- GET /products, GET /products/{id}
- POST /chat, GET/DELETE /chat/history/{session_id}
"""

from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.infrastructure.db.database import get_session as get_db, init_db
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService

from src.application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.domain.exceptions import ProductNotFoundError, ChatServiceError


app = FastAPI(
    title="E-commerce Chat AI",
    description="API de e-commerce de zapatos con chat inteligente (Gemini).",
    version="1.0.0",
)

# CORS básico en desarrollo (ajusta orígenes si lo necesitas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """
    Evento de inicio de la aplicación.

    - Inicializa la base de datos (crea tablas si no existen).
    - Deja la app lista para atender requests.
    """
    init_db()


@app.get("/", summary="Información básica de la API", tags=["Meta"])
def root_info():
    """
    Retorna información general de la API.

    Incluye:
    - Nombre y versión
    - Ruta de documentación (`/docs`)
    - Lista de endpoints disponibles
    - Timestamp UTC
    """
    return {
        "name": "E-commerce Chat AI",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/products", "/products/{id}", "/chat", "/chat/history/{session_id}", "/health"],
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health", summary="Health check", tags=["Meta"])
def health():
    """
    Verifica el estado de la API.

    Returns:
        dict: {"status": "ok", "timestamp": "..."}
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/products", response_model=List[ProductDTO], summary="Lista todos los productos", tags=["Products"])
def list_products(db: Session = Depends(get_db)):
    """
    Lista todos los productos registrados (incluye sin stock).

    Args:
        db (Session): sesión de base de datos inyectada con Depends(get_db).

    Returns:
        List[ProductDTO]: lista de productos.
    """
    service = ProductService(SQLProductRepository(db))
    products = service.get_all_products()
    return [ProductDTO.model_validate(p) for p in products]


@app.get("/products/{product_id}", response_model=ProductDTO, summary="Obtiene un producto por ID", tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto por su ID.

    Args:
        product_id (int): ID del producto.
        db (Session): sesión de base de datos.

    Raises:
        HTTPException(404): si el producto no existe.

    Returns:
        ProductDTO: producto solicitado.
    """
    service = ProductService(SQLProductRepository(db))
    try:
        product = service.get_product_by_id(product_id)
        return ProductDTO.model_validate(product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/chat", response_model=ChatMessageResponseDTO, summary="Procesa un mensaje de chat con IA", tags=["Chat"])
async def chat(request: ChatMessageRequestDTO, db: Session = Depends(get_db)):
    """
    Procesa el mensaje del usuario con ayuda de la IA (Gemini) y persiste el intercambio.

    Flujo:
      1) Lee productos y contexto reciente
      2) Construye prompt y llama al modelo de IA
      3) Guarda mensaje del usuario y del asistente
      4) Retorna respuesta

    Args:
        request (ChatMessageRequestDTO): sesión y texto del usuario
        db (Session): sesión de base de datos

    Raises:
        HTTPException(500): en caso de error interno del servicio de chat

    Returns:
        ChatMessageResponseDTO: con `assistant_message` y metadata
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai = GeminiService()
    service = ChatService(product_repo, chat_repo, ai)

    try:
        response = await service.process_message(request)
        return response
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/chat/history/{session_id}",
    response_model=List[ChatHistoryDTO],
    summary="Obtiene historial de chat por sesión",
    tags=["Chat"],
)
def chat_history(session_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retorna los últimos N mensajes de la sesión, en orden cronológico.

    Args:
        session_id (str): identificador de la sesión de chat
        limit (int): cantidad máxima de mensajes a retornar (default=10)
        db (Session): sesión de base de datos

    Returns:
        List[ChatHistoryDTO]: mensajes en orden cronológico
    """
    chat_repo = SQLChatRepository(db)
    msgs = chat_repo.get_session_history(session_id, limit)
    return [ChatHistoryDTO.model_validate(m) for m in msgs]


@app.delete("/chat/history/{session_id}", summary="Elimina el historial de una sesión", tags=["Chat"])
def delete_history(session_id: str, db: Session = Depends(get_db)):
    """
    Elimina todo el historial de mensajes de una sesión.

    Args:
        session_id (str): identificador de sesión
        db (Session): sesión de base de datos

    Returns:
        dict: {"deleted": <cantidad_de_mensajes_eliminados>}
    """
    chat_repo = SQLChatRepository(db)
    count = chat_repo.delete_session_history(session_id)
    return {"deleted": count}
