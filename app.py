import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Importaciones de Servicios / Controladores ---
from controllers.chat_controller import chat_bp, init_chat_controller
from core.chat_manager import ChatManager
from services.ai_service import AIService
from services.db_service import DBService
from services.user_service import UserService
from services.auth_service import AuthService
from services.session_service import SessionService
# Asumo que tienes un MessageService, si no, es necesario crearlo
from services.message_service import MessageService
from services.auth_middleware import token_required
from utils.text_utils import TextUtils

# --- Importaciones de Modelos ---
from models.dto import CredentialsDTO

# Asume que MessageService también existe y usa DTOs

# Configuración DB y AI
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
    CORS(app)
    text_utils = TextUtils()
    db_service = DBService(config=DB_CONFIG)
    ai_service = AIService(endpoint_url=AI_CONFIG["endpoint_url"], api_key=AI_CONFIG["api_key"])  # IA
    user_service = UserService(db_service=db_service)
    session_service = SessionService(db_service=db_service)
    auth_service = AuthService(user_service=user_service, session_service=session_service)
    message_service = MessageService(db_service=db_service)

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

    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json() or {}
            credentials = CredentialsDTO.from_dict(data)
            credentials.validate_for_registration()
            user = user_service.create_user(credentials)
            return jsonify({
                "ok": True,
                "message": "Usuario registrado exitosamente",
                "user": user.to_dict()
            }), 201
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        except Exception as e:
            return jsonify({"ok": False, "error": f"Error interno: {e}"}), 500

    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json() or {}
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                raise ValueError("Email y contraseña son requeridos")

            user = user_service.authenticate_user(email, password)

            if user:
                try:
                    session_data = auth_service.get_or_create_user_chat_session(user.id)
                    session_id = session_data.get("id")

                except Exception as e:
                    return jsonify({
                        "ok": False,
                        "error": str(e)
                    }), 404
                token = AuthService.generate_token(user.id, user.email)

                return jsonify({
                    "ok": True,
                    "message": "Inicio de sesión exitoso. Sesión retomada.",
                    "token": token,
                    "user": user.to_dict(),
                    "session_id": session_id
                }), 200
            else:
                return jsonify({"ok": False, "error": "Credenciales inválidas"}), 401
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        except Exception as e:
            return jsonify({"ok": False, "error": f"Error interno: {e}"}), 500

    @app.route('/sesiones', methods=['GET'])
    @token_required
    def listar_sesiones():
        user_id = request.user_id
        sesiones = session_service.get_user_sessions(user_id)
        return jsonify({"ok": True, "sesiones": sesiones}), 200

    @app.route('/sesiones', methods=['POST'])
    @token_required
    def crear_sesion():
        user_id = request.user_id
        data = request.get_json() or {}
        titulo = data.get("titulo", "Nueva sesión")
        sesion = session_service.create_session(user_id, titulo)
        return jsonify({"ok": True, "sesion": sesion}), 201

    @app.route('/mensajes/<int:sesion_id>', methods=['GET'])
    @token_required
    def listar_mensajes(sesion_id):
        mensajes = message_service.get_messages_by_session(sesion_id)
        return jsonify({"ok": True, "mensajes": mensajes}), 200

    @app.route('/mensajes', methods=['POST'])
    @token_required
    def enviar_mensaje():
        data = request.get_json() or {}
        user_id = request.user_id
        sesion_id = data.get("sesion_id")
        contenido = data.get("contenido")

        if not sesion_id or not contenido:
            return jsonify({"ok": False, "error": "Datos incompletos"}), 400
        mensaje = message_service.create_message(sesion_id, contenido, f"usuario_{user_id}")
        return jsonify({"ok": True, "mensaje": mensaje}), 201

    @app.route('/usuarios/<int:user_id>', methods=['GET'])
    @token_required
    def obtener_usuario(user_id):
        try:
            usuario = user_service.get_user(user_id)
            return jsonify({"ok": True, "usuario": usuario.to_dict()}), 200
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 404

    @app.route('/usuarios/<int:user_id>', methods=['PUT'])
    @token_required
    def actualizar_usuario(user_id):
        try:
            data = request.get_json() or {}
            usuario = user_service.update_user(user_id, data)
            return jsonify({"ok": True, "usuario": usuario.to_dict()}), 200
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    @app.route('/usuarios/<int:user_id>', methods=['DELETE'])
    @token_required
    def eliminar_usuario(user_id):
        try:
            user_service.delete_user(user_id)
            return jsonify({"ok": True, "message": "Usuario eliminado correctamente"}), 200
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)