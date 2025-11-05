"""
Servicio de IA con Google Gemini.

Lee GEMINI_API_KEY de .env y genera respuestas usando el contexto y los
productos disponibles en el catálogo.
"""

import os
import asyncio
from typing import Iterable, Union
from dotenv import load_dotenv
import google.generativeai as genai
from src.domain.entities import Product, ChatContext

load_dotenv()


class GeminiService:
    """Adaptador del proveedor de IA Google Gemini.

    Configura la clave de API, instancia el modelo y expone la operación
    de generación de contenido a partir de un prompt que incluye:
    catálogo de productos, contexto conversacional y el mensaje del usuario.

    Attributes:
        model_name (str): Nombre del modelo configurado.
        model: Instancia de `genai.GenerativeModel` activa para generar contenido.
    """

    def __init__(self, model_name: str | None = None) -> None:
        """Inicializa el servicio con el modelo especificado o el de .env.

        Si no se especifica un `model_name`, intenta leer `GEMINI_MODEL` de
        archivo de entorno. Como valor por defecto se usa `gemini-2.5-flash`.

        Args:
            model_name (str | None): Nombre del modelo a utilizar.

        Raises:
            RuntimeError: Si `GEMINI_API_KEY` no está configurada.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY no configurada.")
        genai.configure(api_key=api_key)

        # Default moderno (alineado a la guía)
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Instancia del modelo
        self.model = genai.GenerativeModel(self.model_name)

    def format_products_info(self, products: Iterable[Product]) -> str:
        """Formatea la lista de productos para incluirla en el prompt.

        Args:
            products (Iterable[Product]): Productos del catálogo.

        Returns:
            str: Texto con una línea por producto (nombre, marca, precio, etc.).
        """
        lines = [
            f"- {p.name} | {p.brand} | ${p.price:.2f} | Stock: {p.stock} | Talla: {p.size} | Color: {p.color}"
            for p in products
        ]
        return "\n".join(lines) if lines else "- (sin productos)"

    def _build_prompt(
        self,
        user_message: str,
        products: Iterable[Product],
        context: Union[ChatContext, str],
    ) -> str:
        """Construye el prompt consolidando catálogo, instrucciones e historial.

        Acepta `context` como `ChatContext` o como `str` ya formateado.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (Iterable[Product]): Productos disponibles para recomendar.
            context (ChatContext | str): Historial formateado o VO de contexto.

        Returns:
            str: Prompt final que se envía al modelo generativo.
        """
        """
        Acepta `context` como ChatContext o como string ya formateado.
        """
        history = context.format_for_prompt() if isinstance(context, ChatContext) else (context or "")
        products_txt = self.format_products_info(products)

        return (
            "Eres un asistente virtual experto en ventas de zapatos para un e-commerce.\n"
            "Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.\n\n"
            f"PRODUCTOS DISPONIBLES:\n{products_txt}\n\n"
            "INSTRUCCIONES:\n"
            "- Sé amigable y profesional\n"
            "- Usa el contexto de la conversación anterior\n"
            "- Recomienda productos específicos cuando sea apropiado\n"
            "- Menciona precios, tallas y disponibilidad\n"
            "- Si no tienes información, sé honesto\n\n"
            f"{history}\n\n"
            f"Usuario: {user_message}\n\nAsistente:"
        )

    async def generate_response(
        self,
        user_message: str,
        products: Iterable[Product],
        context: Union[ChatContext, str],
    ) -> str:
        """Genera la respuesta del asistente usando el modelo configurado.

        El prompt se arma con el catálogo, el historial (contexto) y el mensaje
        actual del usuario. Internamente ejecuta la llamada de forma no
        bloqueante usando `asyncio.to_thread`.

        Args:
            user_message (str): Texto del usuario.
            products (Iterable[Product]): Productos disponibles.
            context (ChatContext | str): Historial o texto formateado.

        Returns:
            str: Respuesta del asistente (texto no vacío) o un mensaje de fallback.

        Raises:
            Exception: Re-lanza la excepción si no es un caso soportado de
                modelo inexistente/unsupported.
        """
        """
        Genera la respuesta usando el modelo; `context` puede ser ChatContext o str.
        """
        prompt = self._build_prompt(user_message, products, context)

        def _call():
            try:
                resp = self.model.generate_content(prompt)
                text = getattr(resp, "text", "")
                return text.strip() if isinstance(text, str) and text.strip() else "No pude generar una respuesta en este momento."
            except Exception as e:
                # Fallback rápido a un modelo muy compatible si el actual no está habilitado/permitido
                if "not found" in str(e).lower() or "unsupported" in str(e).lower():
                    fallback = "gemini-1.5-flash"
                    self.model = genai.GenerativeModel(fallback)
                    resp2 = self.model.generate_content(prompt)
                    text2 = getattr(resp2, "text", "")
                    return text2.strip() if isinstance(text2, str) and text2.strip() else "No pude generar una respuesta en este momento."
                raise

        return await asyncio.to_thread(_call)

