"""Servicio de aplicación para el chat con IA (Gemini).

Coordina repositorios de productos y de historial de chat con el proveedor
de IA para generar respuestas contextuales y persistir los mensajes."""

from datetime import datetime, UTC
from typing import Optional

from src.application.dtos import (
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
)
from src.domain.entities import ChatContext, ChatMessage
from src.domain.repositories import IChatRepository, IProductRepository


class ChatService:
    """Servicio de aplicación para gestionar el chat con IA.

    Orquesta la interacción entre el repositorio de productos, el repositorio
    de chat y el servicio de IA (por ejemplo, Gemini) para producir respuestas
    con contexto.

    Attributes:
        _product_repo (IProductRepository): Repositorio de productos.
        _chat_repo (IChatRepository): Repositorio de historial de chat.
        _ai_service: Servicio de IA con un método asíncrono
            `generate_response(user_message, products, context) -> str`.
    """

    def __init__(self, product_repo: IProductRepository, chat_repo: IChatRepository, ai_service):
        """Inicializa el servicio con sus dependencias.

        Args:
            product_repo (IProductRepository): Repositorio de productos.
            chat_repo (IChatRepository): Repositorio de historial de chat.
            ai_service: Adaptador del proveedor de IA.
        """
        self._product_repo = product_repo
        self._chat_repo = chat_repo
        self._ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """Procesa un mensaje del usuario y genera una respuesta con IA.

        Flujo:
          1) Obtiene el catálogo de productos.
          2) Recupera los últimos N mensajes de la sesión.
          3) Construye el contexto (`ChatContext`) para el prompt.
          4) Llama al servicio de IA para generar la respuesta.
          5) Persiste el mensaje del usuario y el del asistente.
          6) Retorna un `ChatMessageResponseDTO` con la respuesta.

        Args:
            request (ChatMessageRequestDTO): Mensaje del usuario que incluye `session_id`.

        Returns:
            ChatMessageResponseDTO: Respuesta del asistente y metadatos (timestamp, sesión).

        Raises:
            Exception: Si el proveedor de IA falla o se produce un error inesperado.

        Example:
            >>> req = ChatMessageRequestDTO(session_id="u1", message="Busco zapatillas 42")
            >>> # await chat_service.process_message(req)
        """
        products = self._product_repo.get_all()

        recent = self._chat_repo.get_recent_messages(session_id=request.session_id, count=6)
        context = ChatContext(messages=recent, max_messages=6).format_for_prompt()

        # Llamada a IA (async)
        assistant_text = await self._ai_service.generate_response(
            user_message=request.message,
            products=products,
            context=context,
        )

        # Guardar mensajes
        now = datetime.now(UTC)
        user_msg = ChatMessage(
            id=None, session_id=request.session_id, role="user",
            message=request.message, timestamp=now
        )
        self._chat_repo.save_message(user_msg)

        assistant_msg = ChatMessage(
            id=None, session_id=request.session_id, role="assistant",
            message=assistant_text, timestamp=datetime.utcnow()
        )
        self._chat_repo.save_message(assistant_msg)

        return ChatMessageResponseDTO(
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=assistant_text,
            timestamp=datetime.now(UTC),
        )

    def get_session_history(self, session_id: str, limit: Optional[int] = None):
        """Obtiene el historial de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de la sesión.
            limit (int | None): Límite máximo de mensajes a devolver. Si es None, retorna todos.

        Returns:
            list[ChatMessage]: Mensajes en orden cronológico (antiguo → reciente).
        """
        return self._chat_repo.get_session_history(session_id=session_id, limit=limit)

    def clear_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes de una sesión.

        Args:
            session_id (str): Identificador de la sesión cuyo historial se eliminará.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        return self._chat_repo.delete_session_history(session_id=session_id)
