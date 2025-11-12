from flask import request, jsonify, Blueprint
from core.chat_manager import ChatManager
from models.message_dto import ResponseDTO

chat_bp = Blueprint('chat', __name__)

CHAT_MANAGER: ChatManager = None


def init_chat_controller(manager: ChatManager):
    global CHAT_MANAGER
    CHAT_MANAGER = manager


@chat_bp.route("/api/chat", methods=["POST"])
def chat_endpoint():
    if CHAT_MANAGER is None:
        return jsonify({"success": False, "message": "Servicio de chat no inicializado."}), 500
    data = request.json

    try:
        session_id = int(data.get("session_id"))
        user_message = data.get("message")
    except (TypeError, ValueError):
        return jsonify(ResponseDTO(success=False, message="Datos de entrada inválidos.").data), 400

    if not user_message:
        return jsonify(ResponseDTO(success=False, message="El mensaje no puede estar vacío.").data), 400

    response_dto: ResponseDTO = CHAT_MANAGER.process_user_message(session_id, user_message)

    if response_dto.success:
        return jsonify(response_dto.data), 200
    else:
        status_code = 400 if response_dto.message.startswith("El mensaje no cumple") else 500
        return jsonify({"success": False, "message": response_dto.message}), status_code