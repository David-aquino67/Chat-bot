# Backend/services/message_service.py
from typing import List, Dict, Any
from datetime import datetime
from services.db_service import DBService

class MessageService:
    def __init__(self, db_service: DBService):
        self.db_service = db_service

    def create_message(self, sesion_id: int, contenido: str, remitente: str) -> Dict[str, Any]:
        fecha_envio = datetime.utcnow()
        try:
            msg_id = self.db_service.insert_message(
                sesion_id,
                contenido,
                remitente,
                fecha_envio
            )

            return {
                "id": msg_id,
                "sesion_id": sesion_id,
                "contenido": contenido,
                "remitente": remitente,
                "fecha_envio": fecha_envio.isoformat()
            }
        except Exception as e:
            print(f"Error al crear mensaje: {e}")
            raise Exception("Error en la capa de datos al crear el mensaje.")

    def get_messages_by_session(self, sesion_id: int) -> List[Dict[str, Any]]:
        try:
            mensajes = self.db_service.fetch_messages_by_session(sesion_id)
            return mensajes

        except Exception as e:
            print(f"Error al obtener mensajes: {e}")
            raise Exception("Error en la capa de datos al obtener los mensajes.")