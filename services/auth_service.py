# backend/services/auth_service.py
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any
from services.user_service import UserService
from services.session_service import SessionService

SECRET_KEY = "clave_super_secreta_de_arely"


class AuthService:
    def __init__(self, user_service: UserService, session_service: SessionService):
        self.user_service = user_service
        self.session_service = session_service

    @staticmethod
    def generate_token(user_id: int, email: str) -> str:
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError:
            raise ValueError("El token ha expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")

    def login_user(self, email: str, password: str) -> dict:
        user_dto = self.user_service.authenticate_user(email, password)

        if not user_dto:
            return {"success": False, "message": "Credenciales inválidas"}
        session_data = self.get_or_create_user_chat_session(user_dto.id)
        token = self.generate_token(user_dto.id, user_dto.email)
        return {
            "ok": True,
            "message": "Inicio de sesión exitoso",
            "token": token,
            "user_id": user_dto.id,
            "user": user_dto.to_dict(),
            "session_id": session_data["id"]
        }

    def get_or_create_user_chat_session(self, user_id: int) -> dict:
        active_session = self.session_service.get_active_session_for_user(user_id)

        if active_session:
            print(f"Sesión activa vinculada encontrada: {active_session['id']}")
            return active_session

        else:
            print("ERROR: No se encontró sesión activa vinculada.")
            raise Exception(
                "No se encontró ninguna sesión de chat activa para este usuario. Inicie una nueva sesión manualmente.")