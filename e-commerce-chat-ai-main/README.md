🛍️ Proyecto E-commerce con Chat IA

Este proyecto es un sistema de comercio electrónico inteligente, desarrollado con FastAPI y un asistente de chat con IA integrado.
Permite gestionar productos, consultar información mediante endpoints REST, y mantener una conversación con un asistente virtual que entiende lenguaje natural.

⚙️ Tecnologías Utilizadas

🐍 Python 3.10+

⚡ FastAPI

🧠 IA con modelo conversacional (OpenAI u otro modelo local)

🐳 Docker / Docker Compose

🗃️ SQLite (base de datos)

💻 Uvicorn como servidor ASGI

🚀 Ejecución Local
1️⃣ Clonar el repositorio
git clone https://github.com/TU_USUARIO/e-commerce-chat-ai-lindo.git
cd e-commerce-chat-ai-lindo

2️⃣ Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate     # En Windows
pip install -r requirements.txt

3️⃣ Ejecutar el servidor local
uvicorn main:app --reload

4️⃣ Abrir en navegador
http://localhost:8000/docs

🐳 Ejecución con Docker

Asegúrate de tener Docker y Docker Compose instalados.

1️⃣ Construir la imagen
docker-compose build

2️⃣ Levantar el contenedor
docker-compose up

3️⃣ Verificar que está corriendo

Abre en navegador:

http://localhost:8000/docs

💬 Endpoints Principales
Endpoint	Método	Descripción
/products	GET	Lista todos los productos disponibles
/products/{id}	GET	Muestra la información de un producto específico
/chat	POST	Envía un mensaje al asistente de IA y recibe respuesta
/health	GET	Verifica el estado del servidor
🧾 Documentación del Código

Todo el código está documentado con docstrings en español, explicando el propósito de cada clase, función y endpoint.
Ejemplo:

@app.get("/products")
def obtener_productos():
    """
    Obtiene la lista de productos disponibles en la tienda virtual.
    Retorna un JSON con todos los productos registrados.
    """
    return productos


    👨‍💻 Autor

Nombre: Santiago Mafla
Correo: psmaflaj@eafit.edu.co
Curso: Arquitectura de Software