"""Excepciones de dominio.

Representan errores de negocio (no técnicos) que pueden ocurrir en las
operaciones del catálogo y del chat.
"""


class ProductNotFoundError(Exception):
    """Error lanzado cuando se solicita un producto que no existe.

    Attributes:
        product_id (int | None): Identificador consultado (opcional).
    """

    def __init__(self, product_id: int | None = None):
        """Inicializa el error con un mensaje informativo.

        Args:
            product_id (int | None): Identificador de producto, si se conoce.
        """
        msg = (
            f"Producto con ID {product_id} no encontrado"
            if product_id is not None
            else "Producto no encontrado"
        )
        super().__init__(msg)


class InvalidProductDataError(Exception):
    """Error de validación cuando los datos de un producto son inválidos."""

    def __init__(self, message: str = "Datos de producto inválidos"):
        """Inicializa el error con el detalle de validación.

        Args:
            message (str): Descripción del problema de validación.
        """
        super().__init__(message)


class ChatServiceError(Exception):
    """Error general del servicio de chat."""

    def __init__(self, message: str = "Error en el servicio de chat"):
        """Inicializa el error con un mensaje descriptivo.

        Args:
            message (str): Descripción del problema detectado.
        """
        super().__init__(message)
