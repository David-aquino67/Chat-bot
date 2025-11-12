from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class MessageDTO:
    sesion_id: int
    sender: str
    content: str

    id: Optional[int] = None
    timestamp: datetime = datetime.now()
    tiempo_respuesta: Optional[int] = None

@dataclass
class SessionDTO:
    id: str
    user_id: str
    messages: List[MessageDTO]

@dataclass
class ResponseDTO:
    success: bool
    message: str
    data: Optional[dict] = None