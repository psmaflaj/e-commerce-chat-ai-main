"""
Configuración de la base de datos con SQLAlchemy 2.0.
Lee DATABASE_URL de .env y expone el Engine, SessionLocal y Base.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")

if DATABASE_URL.startswith("sqlite:///"):
    Path("data").mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa para los modelos ORM."""


def get_session():
    """Generador de sesiones de SQLAlchemy para inyección en FastAPI.

    Yields:
        Session: Sesión abierta que se cierra al finalizar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas registradas.

    Importa los modelos para registrar los mapeos y ejecuta
    `Base.metadata.create_all`.
    """
    from . import models  # registra modelos
    Base.metadata.create_all(bind=engine)
