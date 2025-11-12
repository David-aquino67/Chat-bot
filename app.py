from flask import Flask, jsonify

# Capa No Agnóstica (Controlador)
from controllers.chat_controller import chat_bp, init_chat_controller
# Capa Agnóstica (Lógica de Negocio/Task Service)
from core.chat_manager import ChatManager
# Capa Agnóstica (Servicios de Entidad/Proceso)
from services.ai_service import AIService
from services.db_service import DBService
# Capa Agnóstica (Utilidades)
from utils.text_utils import TextUtils

DB_CONFIG = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "chatbot"
}


AI_CONFIG = {
    "endpoint_url": "https://router.huggingface.co/v1/chat/completions",
    "api_key": "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"
}




def create_app():
    app = Flask(__name__)

    text_utils = TextUtils()

    db_service = DBService(config=DB_CONFIG)  # Usa la configuración real de MySQL
    ai_service = AIService(endpoint_url=AI_CONFIG["endpoint_url"], api_key=AI_CONFIG["api_key"])


    chat_manager = ChatManager(
        ai_service=ai_service,
        db_service=db_service,
        text_utils=text_utils
    )


    init_chat_controller(manager=chat_manager)

    app.register_blueprint(chat_bp)

    @app.route("/", methods=["GET"])
    def health_check():
        return jsonify({"status": "OK", "message": "Chatbot API corriendo. Usa /api/chat (POST) para iniciar."}), 200

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(debug=True)