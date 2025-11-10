import time
from typing import List
from models.message_dto import MessageDTO, ResponseDTO, SessionDTO  # DTOs Canónicos
# Importar las interfaces de los Servicios Agnósticos (sin importar su implementación interna)
from services.ai_service import AIService
from services.db_service import DBService
from utils.text_utils import TextUtils


class ChatManager:
    """
    Capa de Lógica de Negocio (Task Service) que orquesta los servicios agnósticos
    para procesar el flujo de una conversación de chat (Recibir, Procesar IA, Guardar, Responder).
    """

    def __init__(self, ai_service: AIService, db_service: DBService, text_utils: TextUtils):
        """
        Inicializa con los servicios agnósticos inyectados (Inyección de Dependencias).
        """
        self.ai_service = ai_service
        self.db_service = db_service
        self.text_utils = text_utils

    def process_user_message(self, session_id: int, user_message: str) -> ResponseDTO:
        """
        Implementa el flujo de negocio completo para una solicitud de chat.
        Flujo: Validar -> Guardar User -> Obtener Contexto -> Consultar IA -> Guardar Bot -> Responder.
        """

        # --- 1. Validar la entrada (Lógica de Negocio + Servicio de Utilidad) [cite: 84, 90] ---
        if not self.text_utils.is_valid(user_message):
            # Regla de Negocio: Decide qué hacer si el texto es inválido
            return ResponseDTO(
                success=False,
                message="El mensaje no cumple con los criterios de validación o seguridad."
            )

        cleaned_message = self.text_utils.clean(user_message)

        try:
            # --- 2. Persistir el mensaje del usuario (Servicio de Entidad DB) [cite: 104] ---
            # Crear DTO para el mensaje del usuario
            user_msg_dto = MessageDTO(
                sesion_id=session_id,
                sender='usuario',
                content=cleaned_message
            )
            # Guardar en la base de datos (se llama al servicio DB encapsulado)
            self.db_service.save_message(user_msg_dto)

            # --- 3. Consultar IA (Servicio de Entidad AI) [cite: 96] ---

            # 3a. Obtener Contexto/Historial (Servicio de Entidad DB)
            # El historial se usa para dar memoria a la IA [cite: 13]
            history: List[MessageDTO] = self.db_service.get_history(session_id, limit=10)

            # 3b. Llamar al servicio de IA encapsulado para generar respuesta
            ai_response_data = self.ai_service.query_ai_model(
                current_message=cleaned_message,
                history=history
            )

            bot_reply = ai_response_data.get("text", "Error: No se pudo generar una respuesta.")
            response_time_ms = ai_response_data.get("latency_ms", 0)

            # --- 4. Persistir la respuesta del bot (Servicio de Entidad DB) [cite: 104] ---
            # Crear DTO para la respuesta del bot, incluyendo el tiempo de respuesta para métricas.
            bot_msg_dto = MessageDTO(
                sesion_id=session_id,
                sender='bot',
                content=bot_reply,
                tiempo_respuesta=response_time_ms
            )
            self.db_service.save_message(bot_msg_dto)

            # --- 5. Devolver la respuesta al usuario (Determina qué información devolver) [cite: 115] ---
            return ResponseDTO(
                success=True,
                message="Mensaje procesado con éxito.",
                data={
                    "session_id": session_id,
                    "reply": bot_reply,
                    "time_ms": response_time_ms
                }
            )

        except Exception as e:
            # Manejo centralizado de errores de la lógica de negocio o servicios subyacentes
            print(f"Error crítico en ChatManager.process_user_message: {e}")
            return ResponseDTO(
                success=False,
                message="Ocurrió un error interno al procesar la solicitud del chat."
            )