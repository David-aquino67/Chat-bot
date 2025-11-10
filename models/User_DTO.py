from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

# DTO para las credenciales de entrada
@dataclass
class CredentialsDTO:
    username: str
    password: str

# DTO para la entidad 'usuario'
@dataclass
class UserDTO:
    id: Optional[int] = None
    nombre_usuario: str
    fecha_creacion: Optional[datetime] = None
    # No incluimos password_hash aquí para no exponer datos sensibles fuera del UserService