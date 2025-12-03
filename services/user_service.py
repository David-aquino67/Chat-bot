import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any
from models.dto import CredentialsDTO, UserDTO
from services.db_service import DBService


class UserService:
    def __init__(self, db_service):
        self.db_service = db_service

    def create_user(self, credentials: CredentialsDTO) -> UserDTO:
        credentials.validate_for_registration()
        existing_user = self.db_service.fetch_user_by_email(credentials.email)
        if existing_user:
            raise ValueError("El correo ya está registrado.")
        hashed_password = bcrypt.hashpw(
            credentials.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        fecha_registro = datetime.utcnow()
        try:
            user_id = self.db_service.insert_user(
                nombre=credentials.nombre_usuario,
                password_hash=hashed_password,
                email=credentials.email,
                fecha_registro=fecha_registro
            )
            return UserDTO(
                id=user_id,
                nombre_usuario=credentials.nombre_usuario,
                email=credentials.email,
                fecha_registro=fecha_registro
            )
        except Exception as e:
            print(f"Error en UserService.create_user: {e}")
            raise Exception("No se pudo crear el usuario debido a un error de base de datos.")

    def authenticate_user(self, email: str, password: str) -> Optional[UserDTO]:
        user: Optional[Dict[str, Any]] = self.db_service.fetch_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            return UserDTO(
                id=user["id"],
                nombre_usuario=user["nombre_usuario"],
                email=user["email"],
                fecha_registro=user["fecha_creacion"]
            )

        return None

    def get_user(self, user_id: int) -> UserDTO:
        row: Optional[Dict[str, Any]] = self.db_service.fetch_user_by_id(user_id)

        if not row:
            raise ValueError("Usuario no encontrado")

        return UserDTO(
            id=row["id"],
            nombre_usuario=row["nombre_usuario"],
            email=row["email"],
            fecha_registro=row["fecha_creacion"]
        )

    def update_user(self, user_id: int, data: dict) -> UserDTO:
        nombre = data.get("nombre")
        email = data.get("email")
        password = data.get("password")
        if not any([nombre, email, password]):
            raise ValueError("No hay datos para actualizar")
        updates = []
        params = []
        if nombre:
            updates.append("nombre = %s")
            params.append(nombre)
        if email:
            updates.append("email = %s")
            params.append(email)
        if password:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            updates.append("password_hash = %s")
            params.append(hashed_pw)
        params.append(user_id)
        updates_str = ", ".join(updates)
        self.db_service.update_user_db(updates_str, tuple(params))
        return self.get_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        try:
            self.db_service.delete_user_db(user_id)
            return True
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            raise Exception("No se pudo eliminar el usuario.")