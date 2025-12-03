import time
from typing import List
from models.message_dto import MessageDTO, ResponseDTO, SessionDTO
from services.ai_service import AIService
from services.db_service import DBService
from utils.text_utils import TextUtils

"""
    Capa de Lógica de Negocio (Task Service) que orquesta los servicios agnósticos
    para procesar el flujo de una conversación de chat (Recibir, Procesar IA, Guardar, Responder).

    Flujo: Validar -> Guardar User -> Obtener Contexto -> Consultar IA -> Guardar Bot -> Responder
"""


class ChatManager:

    def __init__(self, ai_service: AIService, db_service: DBService, text_utils: TextUtils):
        self.ai_service = ai_service
        self.db_service = db_service
        self.text_utils = text_utils

    def process_user_message(self, session_id: int, user_message: str) -> ResponseDTO:

        if not self.text_utils.is_valid(user_message):
            return ResponseDTO(
                success=False,
                message="El mensaje no cumple con los criterios de validación o seguridad."
            )
        cleaned_message = self.text_utils.clean(user_message)
        try:
            user_msg_dto = MessageDTO(
                sesion_id=session_id,
                sender='usuario',
                content=cleaned_message
            )
            self.db_service.save_message(user_msg_dto)
            history: List[MessageDTO] = self.db_service.get_history(session_id, limit=10)
            ai_response_data = self.ai_service.query_ai_model(
                current_message=cleaned_message,
                history=history
            )
            bot_reply = ai_response_data.get("text", "")
            response_time_ms = ai_response_data.get("latency_ms", 0)
            if bot_reply and not bot_reply.startswith("Error:") and bot_reply.strip():
                bot_msg_dto = MessageDTO(
                    sesion_id=session_id,
                    sender='bot',
                    content=bot_reply,
                    tiempo_respuesta=response_time_ms
                )
                self.db_service.save_message(bot_msg_dto)
                return ResponseDTO(
                    success=True,
                    message="Mensaje procesado con éxito.",
                    data={
                        "session_id": session_id,
                        "reply": bot_reply,
                        "time_ms": response_time_ms
                        }
                )
            else:
                error_message = bot_reply if bot_reply.startswith(
                    "Error:") else "La IA no pudo generar una respuesta válida o la respuesta fue vacía."
                return ResponseDTO(
                    success=False,
                    message=error_message,
                    data={"session_id": session_id}
                )
        except Exception as e:
            print(f"Error crítico en ChatManager.process_user_message: {e}")
            return ResponseDTO(
                success=False,
                message=f"Ocurrió un error interno al procesar la solicitud del chat: {str(e)}"
            )