import mysql.connector
from models.message_dto import MessageDTO, SessionDTO
from datetime import datetime
from typing import List, Optional, Dict, Any


class DBService:
    def __init__(self, config: dict):
        self.config = config
        self.connection = None
        self._connect_to_db()

    def _connect_to_db(self):
        print("Intentando conectar a MySQL...")
        try:
            self.connection = mysql.connector.connect(**self.config)
            print(" Conexión a MySQL establecida con éxito.")
        except mysql.connector.Error as err:
            self.connection = None
            print(f"Error al conectar a MySQL: {err}")
            print("Asegúrate de que MySQL está corriendo y las credenciales son correctas.")
            raise

    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        if not self.connection:
            raise Exception("No hay conexión a la base de datos.")

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.lastrowid
        except mysql.connector.Error as err:
            self.connection.rollback()
            raise err
        finally:
            cursor.close()

    def save_message(self, message: MessageDTO) -> MessageDTO:
        # ... (código save_message existente)
        query = """
        INSERT INTO mensaje (sesion_id, contenido, remitente, tiempo_respuesta, fecha_envio)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            message.sesion_id,
            message.content,
            message.sender,
            message.tiempo_respuesta,
            message.timestamp
        )

        try:
            new_id = self._execute_query(query, params)
            message.id = new_id
            return message
        except Exception as e:
            print(f"Error al guardar mensaje en DB: {e}")
            raise

    def get_history(self, session_id: int, limit: int) -> List[MessageDTO]:
        query = """
        SELECT id, sesion_id, contenido, remitente, fecha_envio, tiempo_respuesta
        FROM mensaje
        WHERE sesion_id = %s
        ORDER BY fecha_envio DESC
        LIMIT %s
        """

        try:
            results = self._execute_query(query, (session_id, limit), fetch_all=True)

            history = []
            if results:
                for row in results:
                    history.append(
                        MessageDTO(
                            id=row['id'],
                            sesion_id=row['sesion_id'],
                            content=row['contenido'],
                            sender=row['remitente'],
                            timestamp=row['fecha_envio'],
                            tiempo_respuesta=row['tiempo_respuesta']
                        )
                    )
            return list(reversed(history))
        except Exception as e:
            print(f"Error al obtener historial de DB: {e}")
            return []

    def insert_message(self, sesion_id: int, contenido: str, remitente: str, fecha_envio: datetime) -> int:
        query = """
        INSERT INTO Mensaje (sesion_id, contenido, remitente, fecha_envio)
        VALUES (%s, %s, %s, %s)
        """
        params = (
            sesion_id,
            contenido,
            remitente,
            fecha_envio.strftime('%Y-%m-%d %H:%M:%S')
        )
        return self._execute_query(query, params)

    def fetch_messages_by_session(self, sesion_id: int) -> List[Dict[str, Any]]:
        query = """
        SELECT id, sesion_id, contenido, remitente, fecha_envio 
        FROM Mensaje 
        WHERE sesion_id = %s 
        ORDER BY fecha_envio ASC
        """
        return self._execute_query(query, (sesion_id,), fetch_all=True)


    def create_session(self, user_id: int, title: str = "Nueva Conversación") -> SessionDTO:
        query = """
        INSERT INTO sesion (usuario_id, titulo, estado)
        VALUES (%s, %s, %s)
        """
        params = (user_id, title, 'activa')

        try:
            new_id = self._execute_query(query, params)
            return SessionDTO(id=new_id, user_id=user_id, titulo=title, messages=[])
        except Exception as e:
            print(f"Error al crear sesión: {e}")
            raise

    def fetch_user_sessions(self, user_id: int) -> List[dict]:
        query = """
        SELECT id, titulo, fecha_inicio 
        FROM Sesion 
        WHERE usuario_id = %s 
        ORDER BY fecha_inicio DESC
        """
        try:
            return self._execute_query(query, (user_id,), fetch_all=True)
        except Exception as e:
            print(f"Error al obtener sesiones de DB: {e}")
            raise

    def fetch_active_session(self, user_id: int) -> Optional[dict]:
        query = """
        SELECT id, titulo, fecha_inicio 
        FROM Sesion 
        WHERE usuario_id = %s AND estado = 'activa'
        ORDER BY fecha_inicio DESC
        LIMIT 1
        """
        try:
            return self._execute_query(query, (user_id,), fetch_one=True)
        except Exception as e:
            print(f"Error al obtener sesión activa de DB: {e}")
            raise

    def fetch_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT id, nombre_usuario, email, fecha_creacion, password_hash FROM Usuario WHERE email = %s"
        return self._execute_query(query, (email,), fetch_one=True)

    def insert_user(self, nombre: str, password_hash: str, email: str, fecha_registro: datetime) -> int:
        query = """
        INSERT INTO Usuario (nombre_usuario, password_hash, fecha_creacion, email)
        VALUES (%s, %s, %s, %s)
        """
        params = (
            nombre,
            password_hash,
            fecha_registro.strftime('%Y-%m-%d %H:%M:%S'),
            email
        )
        return self._execute_query(query, params)

    def fetch_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT id, nombre_usuario, email, fecha_creacion, password_hash FROM Usuario WHERE id = %s"
        return self._execute_query(query, (user_id,), fetch_one=True)

    def update_user_db(self, updates: str, params: tuple) -> None:
        sql = f"UPDATE Usuario SET {updates} WHERE id = %s"
        self._execute_query(sql, params)

    def delete_user_db(self, user_id: int) -> None:
        query = "DELETE FROM Usuario WHERE id = %s"
        self._execute_query(query, (user_id,))