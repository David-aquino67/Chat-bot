from flask import request, jsonify, Blueprint
from core.chat_manager import ChatManager
from models.message_dto import ResponseDTO  # Para manejar el tipo de retorno

# Creamos un Blueprint para organizar las rutas de la API (es buena práctica en Flask)
chat_bp = Blueprint('chat', __name__)

# La instancia del ChatManager se inyectará al registrar el Blueprint en app.py
CHAT_MANAGER: ChatManager = None


def init_chat_controller(manager: ChatManager):
    """Función para inyectar la dependencia del ChatManager."""
    global CHAT_MANAGER
    CHAT_MANAGER = manager


@chat_bp.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """
    Expone la ruta REST para enviar mensajes.
    No contiene lógica de negocio, solo invoca el servicio encapsulado.
    """
    if CHAT_MANAGER is None:
        return jsonify({"success": False, "message": "Servicio de chat no inicializado."}), 500

    # 1. Adaptar/Mapear la entrada JSON (Dependiente del protocolo Flask)
    data = request.json

    # Asumimos que el cliente envía 'session_id' (int) y 'message' (str)
    try:
        session_id = int(data.get("session_id"))
        user_message = data.get("message")
    except (TypeError, ValueError):
        return jsonify(ResponseDTO(success=False, message="Datos de entrada inválidos.").data), 400

    if not user_message:
        return jsonify(ResponseDTO(success=False, message="El mensaje no puede estar vacío.").data), 400

    # 2. Invocar la Lógica de Negocio Agnóstica
    # El manager recibe parámetros simples, pero usa DTOs internamente.
    response_dto: ResponseDTO = CHAT_MANAGER.process_user_message(session_id, user_message)

    # 3. Serializar y devolver la respuesta (Dependiente del protocolo Flask)
    if response_dto.success:
        return jsonify(response_dto.data), 200
    else:
        # Devuelve un error (400 si es del cliente, 500 si es interno)
        status_code = 400 if response_dto.message.startswith("El mensaje no cumple") else 500
        return jsonify({"success": False, "message": response_dto.message}), status_code