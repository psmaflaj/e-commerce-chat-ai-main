"""Entidades de dominio para el e-commerce y el chat.

Contiene las clases de negocio puras: `Product`, `ChatMessage` y `ChatContext`.
Implementan validaciones y utilidades sin depender de frameworks externos.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """Entidad que representa un producto en el e-commerce.

    Esta clase encapsula la lógica de negocio relacionada con productos,
    incluyendo validaciones de nombre, precio y stock, además de utilidades
    para conocer su disponibilidad y modificar inventario.

    Attributes:
        id (Optional[int]): Identificador único del producto.
        name (str): Nombre del producto (no puede ser vacío).
        brand (str): Marca del producto.
        category (str): Categoría del producto (p. ej. Running, Casual).
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio en USD; debe ser mayor a 0.
        stock (int): Unidades disponibles; no puede ser negativo.
        description (str): Descripción corta del producto.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str = ""

    def __post_init__(self):
        """Ejecuta validaciones inmediatamente después de crear la instancia.

        Valida:
          - `name` no puede estar vacío.
          - `price` debe ser mayor a 0.
          - `stock` no puede ser negativo.

        Raises:
            ValueError: Si alguna de las validaciones falla.
        """
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if self.price is None or self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        if self.stock is None or self.stock < 0:
            raise ValueError("El stock no puede ser negativo.")

    def is_available(self) -> bool:
        """Indica si el producto tiene stock disponible.

        Returns:
            bool: `True` si `stock > 0`, de lo contrario `False`.
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """Reduce el stock del producto en la cantidad especificada.

        Args:
            quantity (int): Cantidad a reducir; debe ser positiva.

        Raises:
            ValueError: Si `quantity` es inválida o mayor al stock disponible.
        """
        if quantity is None or quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva.")
        if quantity > self.stock:
            raise ValueError("No hay stock suficiente para la operación.")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Aumenta el stock del producto en la cantidad especificada.

        Args:
            quantity (int): Cantidad a aumentar; debe ser positiva.

        Raises:
            ValueError: Si `quantity` es inválida.
        """
        if quantity is None or quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva.")
        self.stock += quantity


@dataclass
class ChatMessage:
    """Entidad que representa un mensaje en el chat.

    Attributes:
        id (Optional[int]): Identificador del mensaje.
        session_id (str): Identificador de la sesión a la que pertenece el mensaje.
        role (str): Rol del emisor: 'user' o 'assistant'.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Marca de tiempo del mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime

    def __post_init__(self):
        """Valida los campos obligatorios y el rol permitido.

        Valida:
          - `role` ∈ {'user', 'assistant'}.
          - `message` no puede estar vacío.
          - `session_id` no puede estar vacío.

        Raises:
            ValueError: Si alguna validación no se cumple.
        """
        if self.role not in {"user", "assistant"}:
            raise ValueError("El rol debe ser 'user' o 'assistant'.")
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío.")

    def is_from_user(self) -> bool:
        """Indica si el mensaje fue enviado por el usuario.

        Returns:
            bool: `True` si `role == 'user'`, de lo contrario `False`.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """Indica si el mensaje fue enviado por el asistente.

        Returns:
            bool: `True` si `role == 'assistant'`, de lo contrario `False`.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """Value Object que encapsula el contexto de una conversación.

    Mantiene los mensajes recientes para dar coherencia al chat y ofrece
    utilidades para formatearlos según el estilo requerido por el LLM.

    Attributes:
        messages (list[ChatMessage]): Mensajes de la conversación.
        max_messages (int): Número máximo de mensajes a considerar.
    """

    messages: list[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> list[ChatMessage]:
        """Obtiene los últimos `max_messages` mensajes del contexto.

        Returns:
            list[ChatMessage]: Sublista con los mensajes más recientes.
        """
        return self.messages[-self.max_messages :]

    def format_for_prompt(self) -> str:
        """Formatea los últimos mensajes para construir el prompt del LLM.

        Convierte los mensajes a líneas con prefijos `user:` / `assistant:` en
        orden cronológico, normalizando posibles variantes del rol.

        Returns:
            str: Texto multilínea con el historial formateado.
        """
        msgs = self.messages[-self.max_messages:] if self.max_messages else self.messages

        role_map = {
            "user": "user",
            "assistant": "assistant",
            "usuario": "user",
            "asistente": "assistant",
        }

        lines = []
        for m in msgs:
            raw_role = (m.role or "").strip().lower()
            role = role_map.get(raw_role, "user")  # por defecto 'user' si es desconocido
            lines.append(f"{role}: {m.message}")

        return "\n".join(lines)

