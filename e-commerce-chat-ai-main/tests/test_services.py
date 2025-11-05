"""Tests de servicios de aplicación (ProductService y ChatService).

Usan repositorios y proveedores de IA en memoria para validar:
- CRUD y filtros de productos,
- flujo feliz de chat (persistencia user+assistant),
- propagación o encapsulamiento de errores de IA.
"""

import asyncio
import pytest
from typing import List, Optional
from datetime import datetime

from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import ProductDTO, ChatMessageRequestDTO
from src.domain.repositories import IProductRepository, IChatRepository
from src.domain.entities import Product, ChatMessage
from src.domain.exceptions import ProductNotFoundError, InvalidProductDataError

# Nota: tu ChatService puede no envolver errores en ChatServiceError; por eso probamos Exception genérica también.
try:
    from src.domain.exceptions import ChatServiceError
    CHAT_ERROR_TYPES = (ChatServiceError, Exception)
except Exception:
    CHAT_ERROR_TYPES = (Exception,)


# ─────────────── Fakes en memoria ───────────────

class FakeProductRepo(IProductRepository):
    """Repositorio de productos en memoria para pruebas unitarias."""

    def __init__(self):
        """Inicializa el almacenamiento con dos productos base."""
        self._data: List[Product] = [
            Product(id=1, name="Pegasus", brand="Nike", category="Running", size="42", color="Negro", price=120.0, stock=5),
            Product(id=2, name="Ultraboost", brand="Adidas", category="Running", size="42", color="Blanco", price=150.0, stock=0),
        ]

    def get_all(self) -> List[Product]:
        """Retorna todos los productos."""
        return list(self._data)

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Busca por ID en la lista en memoria."""
        return next((p for p in self._data if p.id == product_id), None)

    def get_by_brand(self, brand: str) -> List[Product]:
        """Filtra por marca exacta."""
        return [p for p in self._data if p.brand == brand]

    def get_by_category(self, category: str) -> List[Product]:
        """Filtra por categoría exacta."""
        return [p for p in self._data if p.category == category]

    def save(self, product: Product) -> Product:
        """Inserta o actualiza un producto en memoria."""
        if product.id is None:
            product.id = max(p.id for p in self._data) + 1
            self._data.append(product)
            return product
        for i, p in enumerate(self._data):
            if p.id == product.id:
                self._data[i] = product
                return product
        # si no existía, se inserta
        self._data.append(product)
        return product

    def delete(self, product_id: int) -> bool:
        """Elimina un producto por ID."""
        before = len(self._data)
        self._data = [p for p in self._data if p.id != product_id]
        return len(self._data) < before


class FakeChatRepo(IChatRepository):
    """Repositorio de historial de chat en memoria para pruebas unitarias."""

    def __init__(self):
        """Inicializa lista de mensajes vacía."""
        self._msgs: list[ChatMessage] = []

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda el mensaje asignando ID incrementado."""
        message.id = (max([m.id for m in self._msgs if m.id] + [0]) + 1)
        self._msgs.append(message)
        return message

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """Obtiene historial por sesión; respeta el límite si se indica."""
        items = [m for m in self._msgs if m.session_id == session_id]
        return items if limit is None else items[-limit:]

    def delete_session_history(self, session_id: str) -> int:
        """Elimina todo el historial de la sesión especificada."""
        before = len(self._msgs)
        self._msgs = [m for m in self._msgs if m.session_id != session_id]
        return before - len(self._msgs)

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Devuelve los últimos N mensajes (orden cronológico ascendente)."""
        items = [m for m in self._msgs if m.session_id == session_id]
        return items[-count:]


class FakeAI:
    """Proveedor de IA falso que devuelve un prefijo indicativo en la respuesta."""

    async def generate_response(self, user_message: str, products, context: str) -> str:
        """Devuelve una respuesta controlada con conteo de productos."""
        return f"[AI] {user_message} ({len(products)} productos)"


class FailingAI:
    """Proveedor de IA que simula un fallo para probar la propagación de errores."""

    async def generate_response(self, user_message: str, products, context: str) -> str:
        """Lanza un RuntimeError simulando indisponibilidad del servicio."""
        raise RuntimeError("IA caída")


# ─────────────── Tests de ProductService ───────────────

def test_product_service_crud_and_filters():
    """Valida CRUD básico y búsqueda por filtros en ProductService."""
    svc = ProductService(FakeProductRepo())

    # listar
    allp = svc.get_all_products()
    assert len(allp) == 2

    # crear
    dto = ProductDTO(
        name="VaporFly", brand="Nike", category="Running",
        size="42", color="Azul", price=200.0, stock=3, description="Ligera"
    )
    created = svc.create_product(dto)
    assert created.id == 3

    # get por ID
    assert svc.get_product_by_id(1).name == "Pegasus"
    with pytest.raises(ProductNotFoundError):
        svc.get_product_by_id(999)

    # buscar por filtros
    nike = svc.search_products({"brand": "Nike"})
    assert all(p.brand == "Nike" for p in nike)

    # disponibles
    avail = svc.get_available_products()
    assert all(p.stock > 0 for p in avail)

    # update
    upd = ProductDTO(
        name="VaporFly NEXT%", brand="Nike", category="Running",
        size="42", color="Azul", price=210.0, stock=2, description="Act."
    )
    updated = svc.update_product(created.id, upd)
    assert updated.price == 210.0 and updated.stock == 2

    # delete
    assert svc.delete_product(created.id) is True
    with pytest.raises(ProductNotFoundError):
        svc.delete_product(999)


def test_product_service_invalid_data():
    """Valida que create_product lance error con datos inválidos."""
    svc = ProductService(FakeProductRepo())
    bad = ProductDTO(
        name="", brand="Nike", category="Running",
        size="42", color="Azul", price=120.0, stock=1, description=""
    )
    with pytest.raises(InvalidProductDataError):
        svc.create_product(bad)


# ─────────────── Tests de ChatService ───────────────

def test_chat_service_ok_flow_saves_messages_and_returns_dto():
    """Valida flujo feliz: guarda user+assistant y retorna DTO con respuesta."""
    product_repo = FakeProductRepo()
    chat_repo = FakeChatRepo()
    ai = FakeAI()
    svc = ChatService(product_repo, chat_repo, ai)

    req = ChatMessageRequestDTO(session_id="s1", message="hola")
    res = asyncio.run(svc.process_message(req))

    assert res.session_id == "s1"
    assert "[AI] hola" in res.assistant_message
    # se guardaron 2 mensajes (user + assistant)
    history = chat_repo.get_session_history("s1")
    assert len(history) == 2
    assert history[0].role == "user" and history[1].role == "assistant"


def test_chat_service_ai_error_is_propagated_or_wrapped():
    """Valida que errores del proveedor de IA se propaguen o se envuelvan."""
    product_repo = FakeProductRepo()
    chat_repo = FakeChatRepo()
    ai = FailingAI()
    svc = ChatService(product_repo, chat_repo, ai)

    req = ChatMessageRequestDTO(session_id="s1", message="hola")
    with pytest.raises(CHAT_ERROR_TYPES):
        asyncio.run(svc.process_message(req))
