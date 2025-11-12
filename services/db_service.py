import mysql.connector
from typing import List, Optional
from models.message_dto import MessageDTO, SessionDTO
from datetime import datetime


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