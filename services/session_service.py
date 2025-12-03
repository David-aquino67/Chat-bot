# Backend/services/session_service.py
from datetime import datetime
from typing import List, Dict, Any, Optional
from services.db_service import DBService
from models.message_dto import SessionDTO


class SessionService:
    def __init__(self, db_service: DBService):
        self.db_service = db_service

    def create_session(self, usuario_id: int, titulo: str) -> SessionDTO:
        try:
            new_session_dto = self.db_service.create_session(usuario_id, titulo)
            return new_session_dto
        except Exception as e:
            print(f"Error en SessionService.create_session: {e}")
            raise Exception("No se pudo crear la sesión.")

    def get_user_sessions(self, usuario_id: int) -> List[Dict[str, Any]]:
        try:
            sesiones = self.db_service.fetch_user_sessions(usuario_id)
            return sesiones
        except Exception as e:
            print(f"Error en SessionService.get_user_sessions: {e}")
            raise Exception("No se pudo obtener el historial de sesiones.")

    def get_active_session_for_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.db_service.fetch_active_session(user_id)

