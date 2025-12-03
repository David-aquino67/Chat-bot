from dataclasses import dataclass, field, asdict
from datetime import datetime
import re
from typing import Optional, Dict, Any

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


@dataclass
class CredentialsDTO:
    email: str
    password: str
    nombre_usuario: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CredentialsDTO":
        email = data.get("email") or data.get("correo") or ""
        password = data.get("password") or data.get("contrasena") or data.get("contraseña") or ""
        nombre_usuario = data.get("nombre") or data.get("username") or data.get("user") or None

        return CredentialsDTO(
            email=email.strip(),
            password=password,
            nombre_usuario=nombre_usuario.strip() if nombre_usuario else None
        )

    def validate_for_registration(self) -> None:
        if not self.nombre_usuario:
            raise ValueError("El campo 'nombre' es requerido para el registro.")
        self._validate_email_and_password()

    def validate_for_login(self) -> None:
        self._validate_email_and_password()

    def _validate_email_and_password(self) -> None:
        if not self.email:
            raise ValueError("El campo 'email' es requerido.")
        if not EMAIL_RE.match(self.email):
            raise ValueError("Formato de correo inválido.")
        if not self.password:
            raise ValueError("El campo 'password' es requerido.")
        if len(self.password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")


@dataclass
class UserDTO:
    id: Optional[int]
    nombre_usuario: str
    email: str
    fecha_registro: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> "UserDTO":
        fecha = row.get("fecha_registro") or row.get("created_at") or row.get("fecha") or None
        if isinstance(fecha, str):
            try:
                fecha = datetime.fromisoformat(fecha)
            except Exception:
                fecha = datetime.utcnow()
        elif fecha is None:
            fecha = datetime.utcnow()

        return UserDTO(
            id=int(row.get("id")) if row.get("id") is not None else None,
            nombre_usuario=str(row.get("nombre_usuario") or ""),
            email=str(row.get("email") or ""),
            fecha_registro=row.get("fecha_creacion") or datetime.utcnow()
        )

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre_usuario,
            "email": self.email,
            "fecha_registro": self.fecha_registro.isoformat()
        }