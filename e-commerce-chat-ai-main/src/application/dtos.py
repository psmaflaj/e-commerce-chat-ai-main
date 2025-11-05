"""Objetos de transferencia de datos (DTOs) para la capa de aplicación.

Define estructuras de entrada/salida para productos y chat. Los DTOs se
validan con Pydantic v2 y sirven como contrato estable entre la API y los
servicios de aplicación.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from pydantic import ConfigDict


class ProductDTO(BaseModel):
    """DTO para productos del catálogo.

    Attributes:
        id (Optional[int]): Identificador del producto (opcional en creación).
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría (por ejemplo, Running, Casual).
        size (str): Talla.
        color (str): Color.
        price (float): Precio en USD; debe ser mayor a 0.
        stock (int): Unidades disponibles; no puede ser negativo.
        description (str): Descripción breve del producto.
    """
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        """Valida que el precio sea mayor a cero.

        Args:
            v (float): Valor del precio.

        Raises:
            ValueError: Si el precio es None o no es mayor a 0.

        Returns:
            float: Precio validado.
        """
        if v is None or v <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        """Valida que el stock no sea negativo.

        Args:
            v (int): Unidades en inventario.

        Raises:
            ValueError: Si el stock es None o es menor que 0.

        Returns:
            int: Stock validado.
        """
        if v is None or v < 0:
            raise ValueError("El stock no puede ser negativo.")
        return v


class ChatMessageRequestDTO(BaseModel):
    """DTO de entrada para el endpoint de chat.

    Attributes:
        session_id (str): Identificador de sesión del usuario.
        message (str): Texto enviado por el usuario.
    """
    session_id: str
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Valida que el mensaje no esté vacío o en blanco."""
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        return v

    @field_validator("session_id")
    @classmethod
    def session_id_not_empty(cls, v: str) -> str:
        """Valida que el identificador de sesión no esté vacío o en blanco."""
        if not v or not v.strip():
            raise ValueError("El session_id no puede estar vacío.")
        return v


class ChatMessageResponseDTO(BaseModel):
    """DTO de salida para respuestas del chat.

    Attributes:
        session_id (str): Identificador de sesión.
        user_message (str): Mensaje del usuario.
        assistant_message (str): Respuesta generada por la IA.
        timestamp (datetime): Marca de tiempo de la respuesta.
    """
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """DTO para mostrar mensajes del historial de chat.

    Attributes:
        id (int): Identificador del mensaje.
        role (str): Rol del emisor ('user' o 'assistant').
        message (str): Contenido del mensaje.
        timestamp (datetime): Fecha y hora de creación.
    """
    id: int
    role: str
    message: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
