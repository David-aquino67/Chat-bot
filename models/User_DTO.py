from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class CredentialsDTO:
    username: str
    password: str

@dataclass
class UserDTO:
    id: Optional[int] = None
    nombre_usuario: str
    fecha_creacion: Optional[datetime] = None