from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


# DTO para la entidad 'mensaje'
@dataclass
class MessageDTO:
    """Representa el formato canónico de un mensaje de chat."""

    # --- 1. CAMPOS SIN VALOR POR DEFECTO (OBLIGATORIOS) ---
    sesion_id: int  # La sesión a la que pertenece
    sender: str  # 'usuario' o 'bot'
    content: str  # El texto del mensaje

    # --- 2. CAMPOS CON VALOR POR DEFECTO (OPCIONALES) ---
    id: Optional[int] = None  # ID del mensaje (asignado por DB)
    timestamp: datetime = datetime.now()
    tiempo_respuesta: Optional[int] = None  # En ms


# ... (El resto de tus DTOs, como SessionDTO y ResponseDTO, pueden permanecer como están)


# DTO para una conversación completa (contexto)
@dataclass
class SessionDTO:
    """Representa el formato canónico de una sesión de conversación."""
    id: str
    user_id: str
    messages: List[MessageDTO]


# DTO genérico para la respuesta de cualquier servicio (éxito/error)
@dataclass
class ResponseDTO:
    success: bool
    message: str
    data: Optional[dict] = None