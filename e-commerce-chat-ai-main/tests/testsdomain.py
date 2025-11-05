"""Tests adicionales de dominio.

Incluye pruebas de invariantes de Product, validación de datos inválidos y
formateo de contexto de chat. Sirve como complemento a test_entities.py.
"""

from datetime import datetime
import pytest

from src.domain.entities import Product, ChatMessage, ChatContext

# Si ya hiciste excepciones personalizadas, importa:
try:
    from src.domain.exceptions import InvalidProductDataError
except Exception:
    InvalidProductDataError = ValueError  # fallback si aún no la usas


def test_product_invariants_and_stock_ops():
    """Product: invariantes de disponibilidad y operaciones de stock."""
    p = Product(
        id=None, name="Air Zoom Pegasus", brand="Nike", category="Running",
        size="42", color="Negro", price=120.0, stock=5, description="Zapatilla running"
    )
    assert p.is_available() is True

    p.reduce_stock(2)
    assert p.stock == 3

    p.increase_stock(4)
    assert p.stock == 7

    with pytest.raises((ValueError, InvalidProductDataError)):
        p.reduce_stock(0)
    with pytest.raises((ValueError, InvalidProductDataError)):
        p.reduce_stock(9999)
    with pytest.raises((ValueError, InvalidProductDataError)):
        p.increase_stock(0)


def test_product_invalid_data():
    """Product: combinaciones inválidas de datos deben fallar en construcción."""
    with pytest.raises((ValueError, InvalidProductDataError)):
        Product(id=None, name="", brand="Nike", category="Running", size="42", color="Negro", price=120.0, stock=1)
    with pytest.raises((ValueError, InvalidProductDataError)):
        Product(id=None, name="X", brand="Nike", category="Running", size="42", color="Negro", price=-1, stock=1)
    with pytest.raises((ValueError, InvalidProductDataError)):
        Product(id=None, name="X", brand="Nike", category="Running", size="42", color="Negro", price=10, stock=-5)


def test_chatmessage_valid_and_invalid_roles():
    """ChatMessage: roles válidos e inválidos."""
    ChatMessage(id=None, session_id="s1", role="user", message="hola", timestamp=datetime.utcnow())
    ChatMessage(id=None, session_id="s1", role="assistant", message="¡hola!", timestamp=datetime.utcnow())
    with pytest.raises(ValueError):
        ChatMessage(id=None, session_id="s1", role="system", message="no permitido", timestamp=datetime.utcnow())


def test_chatcontext_recent_and_format():
    """ChatContext: slicing de últimos 6 y formateo con prefijos legibles."""
    # 8 mensajes alternando roles para que el VO haga slicing a los últimos 6
    messages = []
    for i in range(8):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append(ChatMessage(id=None, session_id="s1", role=role, message=f"m{i}", timestamp=datetime.utcnow()))

    ctx = ChatContext(messages=messages, max_messages=6)
    recent = ctx.get_recent_messages()
    assert len(recent) == 6
    assert recent[0].message == "m2" and recent[-1].message == "m7"

    prompt = ctx.format_for_prompt()
    # Debe contener solo m2..m7 y prefijos "Usuario"/"Asistente"
    assert "Usuario: m2" in prompt
    assert "Asistente: m3" in prompt
    assert "m0" not in prompt and "m1" not in prompt
