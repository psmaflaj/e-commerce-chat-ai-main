"""
Carga de datos iniciales para la base de datos.

Regla del taller:
- Si no existen productos, se deben crear 10 productos de ejemplo
  (marcas variadas, categorías Running/Casual/Formal, precios 50–200, stock variado).
"""

from src.infrastructure.db.database import init_db, SessionLocal
from src.infrastructure.db.models import ProductModel


def load_initial_data() -> int:
    """Crea tablas (si no existen) y carga 10 productos si la tabla está vacía.

    Returns:
        int: Cantidad de productos insertados en esta ejecución.
    """
    init_db()
    db = SessionLocal()
    inserted = 0
    try:
        if db.query(ProductModel).count() == 0:
            products = [
                ProductModel(name="Pegasus 40",        brand="Nike",        category="Running", size="42", color="Negro", price=120.0, stock=8,  description="Running diaria"),
                ProductModel(name="Ultraboost Light",  brand="Adidas",      category="Running", size="42", color="Blanco", price=150.0, stock=5,  description="Amortiguación premium"),
                ProductModel(name="Suede Classic",     brand="Puma",        category="Casual",  size="41", color="Azul",   price=80.0,  stock=12, description="Clásico de gamuza"),
                ProductModel(name="Classic Leather",   brand="Reebok",      category="Casual",  size="42", color="Blanco", price=90.0,  stock=10, description="Clásico urbano"),
                ProductModel(name="Fresh Foam 1080",   brand="New Balance", category="Running", size="42", color="Gris",   price=160.0, stock=6,  description="Amortiguación suave"),
                ProductModel(name="Gel-Cumulus 25",    brand="ASICS",       category="Running", size="42", color="Azul",   price=140.0, stock=7,  description="Entrenamiento diario"),
                ProductModel(name="Madrid",            brand="Hush Puppies",category="Formal",  size="42", color="Café",   price=110.0, stock=4,  description="Zapato de vestir"),
                ProductModel(name="Chuck 70",          brand="Converse",    category="Casual",  size="42", color="Negro",  price=75.0,  stock=15, description="Clásica lona"),
                ProductModel(name="Old Skool",         brand="Vans",        category="Casual",  size="42", color="Negro",  price=70.0,  stock=20, description="Skate clásico"),
                ProductModel(name="Go Run Ride 11",    brand="Skechers",    category="Running", size="42", color="Rojo",   price=95.0,  stock=9,  description="Ligero y cómodo"),
            ]
            db.add_all(products)
            db.commit()
            inserted = len(products)
        return inserted
    finally:
        db.close()


if __name__ == "__main__":
    n = load_initial_data()
    print(f"Init data: {n} productos insertados." if n else "Init data: ya había productos, no se insertó nada." )
