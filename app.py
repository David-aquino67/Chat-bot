from flask import Flask, jsonify

# 1. Importar todos los componentes
# Capa No Agnóstica (Controlador)
from controllers.chat_controller import chat_bp, init_chat_controller
# Capa Agnóstica (Lógica de Negocio/Task Service)
from core.chat_manager import ChatManager
# Capa Agnóstica (Servicios de Entidad/Proceso)
from services.ai_service import AIService
from services.db_service import DBService
# Capa Agnóstica (Utilidades)
from utils.text_utils import TextUtils

# --- Configuración de Clientes/Servicios (Agnósticos) ---

# Configuración de Conexión a Base de Datos MySQL
# NOTA: Debes reemplazar 'tu_usuario_mysql' y 'tu_password_mysql' con tus credenciales.
DB_CONFIG = {
    "user": "tu_usuario_mysql",
    "password": "tu_password_mysql",
    "host": "localhost",
    "database": "chatbot"
}

# Configuración del Cliente de Inferencia de IA (para Mistral-7B)
AI_CONFIG = {
    "endpoint_url": "https://tu-endpoint-de-inferencia-mistral.com/generate",
    "api_key": "hf_tu_token_de_acceso_a_hf"
}


# La clase AIService tomará 'endpoint_url' y 'api_key' de este diccionario.


def create_app():
    app = Flask(__name__)

    # ----------------------------------------------------------------------
    # --- FASE 1: Creación de Implementaciones de Servicios Agnósticos ---
    # ----------------------------------------------------------------------

    # Utilidades (Abstracción de Utilidad)
    text_utils = TextUtils()

    # Servicios de Entidad/Proceso (Abstracción de Entidad/Proceso)
    # Aquí es donde se conectan los servicios con sus clientes reales (DB, IA, etc.)
    db_service = DBService(config=DB_CONFIG)  # Usa la configuración real de MySQL
    ai_service = AIService(endpoint_url=AI_CONFIG["endpoint_url"], api_key=AI_CONFIG["api_key"])
    # auth_service = AuthService(...) # Se implementaría aquí

    # ----------------------------------------------------------------------
    # --- FASE 2: Creación del Task Service (Lógica de Negocio) ---
    # ----------------------------------------------------------------------

    # El ChatManager es el orquestador que recibe todos los servicios por inyección.
    chat_manager = ChatManager(
        ai_service=ai_service,
        db_service=db_service,
        text_utils=text_utils
    )

    # ----------------------------------------------------------------------
    # --- FASE 3: Conexión de la Capa No Agnóstica (Presentación) ---
    # ----------------------------------------------------------------------

    # 3a. Inyectar el manager en el controlador antes de registrar la ruta
    init_chat_controller(manager=chat_manager)

    # 3b. Registrar el Blueprint con todas las rutas de chat (ej: /api/chat)
    app.register_blueprint(chat_bp)

    # Ruta básica de salud (GET /)
    @app.route("/", methods=["GET"])
    def health_check():
        return jsonify({"status": "OK", "message": "Chatbot API corriendo. Usa /api/chat (POST) para iniciar."}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    # Ejecutar la aplicación Flask
    # NOTA: Flask ya asume FLASK_APP=app.py si no lo especificas en el entorno.
    app.run(debug=True)