"""Servicios de aplicación para la gestión de productos.

Orquesta casos de uso sobre `IProductRepository`, aplicando validaciones
de negocio y transformaciones desde/hacia DTOs.
"""

from typing import Any, Dict, List, Optional

from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError, ProductNotFoundError
from src.domain.repositories import IProductRepository
from .dtos import ProductDTO


class ProductService:
    """Servicio de aplicación para gestionar productos del catálogo.

    Usa un `IProductRepository` para persistir y consultar productos,
    aplicando validaciones de negocio y transformaciones desde/hacia DTOs.

    Attributes:
        _repo (IProductRepository): Repositorio de productos inyectado.
    """

    def __init__(self, repo: IProductRepository):
        """Inicializa el servicio con su repositorio.

        Args:
            repo (IProductRepository): Repositorio concreto de productos.
        """
        self._repo = repo

    def get_all_products(self) -> List[Product]:
        """Retorna todos los productos registrados.

        Returns:
            List[Product]: Lista completa de productos.
        """
        return self._repo.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """Obtiene un producto por su identificador.

        Args:
            product_id (int): Identificador del producto a consultar.

        Raises:
            ProductNotFoundError: Si no existe un producto con ese ID.

        Returns:
            Product: Entidad del producto encontrado.
        """
        prod = self._repo.get_by_id(product_id)
        if prod is None:
            raise ProductNotFoundError(product_id)
        return prod

    def search_products(self, filters: Optional[Dict[str, Any]] = None) -> List[Product]:
        """Busca productos según filtros simples.

        Soporta filtros por:
          - brand
          - category
        Otros filtros (size, color, min_price, max_price) se aplican en memoria.

        Args:
            filters (dict | None): Diccionario de criterios de búsqueda.

        Returns:
            List[Product]: Resultados que cumplen con los filtros.
        """
        filters = filters or {}
        brand = filters.get("brand")
        category = filters.get("category")

        # Usa los métodos del repositorio cuando existan
        if brand and category:
            # Intersección simple
            by_brand = {p.id: p for p in self._repo.get_by_brand(brand)}
            result = [p for p in self._repo.get_by_category(category) if p.id in by_brand]
        elif brand:
            result = self._repo.get_by_brand(brand)
        elif category:
            result = self._repo.get_by_category(category)
        else:
            result = self._repo.get_all()

        # Filtros opcionales en memoria
        size = filters.get("size")
        color = filters.get("color")
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")

        def ok(p: Product) -> bool:
            if size and p.size != size:
                return False
            if color and p.color != color:
                return False
            if min_price is not None and p.price < float(min_price):
                return False
            if max_price is not None and p.price > float(max_price):
                return False
            return True

        return [p for p in result if ok(p)]

    def create_product(self, product_dto: ProductDTO) -> Product:
        """Crea y persiste un nuevo producto a partir de un DTO.

        Convierte el `ProductDTO` a entidad de dominio `Product` y lo guarda
        mediante el repositorio. Si los datos no son válidos, la entidad de
        dominio lanzará `ValueError`, que se encapsula como `InvalidProductDataError`.

        Args:
            product_dto (ProductDTO): Datos del producto.

        Raises:
            InvalidProductDataError: Si las validaciones del dominio fallan.

        Returns:
            Product: Entidad creada y persistida.
        """
        try:
            prod = Product(
                id=None,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e)) from e

        return self._repo.save(prod)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> Product:
        """Actualiza un producto existente.

        Valida la existencia previa del producto y luego guarda la entidad
        con los nuevos datos proporcionados por el DTO.

        Args:
            product_id (int): ID del producto a actualizar.
            product_dto (ProductDTO): Datos nuevos.

        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si los datos no son válidos.

        Returns:
            Product: Entidad actualizada.
        """
        existing = self._repo.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id)

        try:
            updated = Product(
                id=product_id,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e)) from e

        return self._repo.save(updated)

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto por su ID.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Raises:
            ProductNotFoundError: Si el producto no existe.

        Returns:
            bool: `True` si se eliminó, `False` en caso contrario.
        """
        existed = self._repo.delete(product_id)
        if not existed:
            raise ProductNotFoundError(product_id)
        return True

    def get_available_products(self) -> List[Product]:
        """Obtiene únicamente productos con stock disponible.

        Returns:
            List[Product]: Productos con `stock > 0`.
        """
        return [p for p in self._repo.get_all() if p.is_available()]
