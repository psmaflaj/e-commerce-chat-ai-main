"""Interfaces (puertos) de repositorios del dominio.

Declaran los contratos para el acceso a productos y para la persistencia
del historial de conversación. Las implementaciones concretas deben vivir
en la capa de infraestructura.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """Contrato de acceso a productos del catálogo."""

    @abstractmethod
    def get_all(self) -> List[Product]:
        """Obtiene todos los productos.

        Returns:
            List[Product]: Colección completa de productos.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Obtiene un producto por ID.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Optional[Product]: Producto encontrado o `None` si no existe.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """Obtiene productos de una marca específica.

        Args:
            brand (str): Marca (p. ej. Nike, Adidas).

        Returns:
            List[Product]: Lista de productos que coinciden con la marca.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """Obtiene productos de una categoría específica.

        Args:
            category (str): Categoría (p. ej. Running, Casual).

        Returns:
            List[Product]: Lista de productos de la categoría indicada.
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Guarda o actualiza un producto.

        Si la entidad no tiene ID, debe crear un nuevo registro y retornar
        la entidad con su ID asignado.

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Entidad persistida (con ID).
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Elimina un producto por su ID.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            bool: `True` si existía y fue eliminado; `False` en caso contrario.
        """
        raise NotImplementedError


class IChatRepository(ABC):
    """Contrato para gestionar el historial de conversaciones (memoria)."""

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Persiste un mensaje del chat.

        Args:
            message (ChatMessage): Mensaje a guardar.

        Returns:
            ChatMessage: Mensaje persistido (con ID, si aplica).
        """
        raise NotImplementedError

    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """Obtiene el historial de una sesión.

        Debe retornar los mensajes en orden cronológico (antiguo → reciente).
        Si `limit` se define, retorna solo los últimos N mensajes manteniendo
        el orden cronológico.

        Args:
            session_id (str): Identificador de la sesión.
            limit (Optional[int]): Límite de mensajes a devolver.

        Returns:
            List[ChatMessage]: Mensajes de la sesión.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """Elimina todo el historial de una sesión.

        Args:
            session_id (str): Identificador de la sesión.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        raise NotImplementedError

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Obtiene los últimos `count` mensajes de una sesión.

        Debe mantener el orden cronológico (antiguo → reciente).

        Args:
            session_id (str): Identificador de la sesión.
            count (int): Cantidad de mensajes recientes a recuperar.

        Returns:
            List[ChatMessage]: Subconjunto de mensajes en orden cronológico.
        """
        raise NotImplementedError
