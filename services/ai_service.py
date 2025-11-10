import time
import requests
from typing import List
from models.message_dto import MessageDTO

# Formato específico para Mistral-7B-Instruct-v0.2
# La plantilla de instrucción envuelve el prompt completo.
MISTRAL_INSTRUCT_TEMPLATE = "[INST] {prompt} [/INST]"


class AIService:
    """
    Servicio Agnóstico para interactuar con el modelo Mistral-7B-Instruct-v0.2.
    """

    def __init__(self, endpoint_url: str, api_key: str):
        # ... (El metodo __init__ ya está definido en la respuesta anterior) ...
        self.endpoint_url = endpoint_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _format_for_mistral(self, history: List[MessageDTO], current_message: str) -> str:
        """
        Adapta el historial de DTOs al formato de prompt de Mistral para mantener el contexto.
        """
        # Este es el paso clave de la 'Memoria' (Contexto conversacional)
        conversation_history = ""
        for msg in history:
            # Creamos una estructura simple para que el modelo identifique los turnos
            role = "USUARIO" if msg.sender == 'usuario' else "ASISTENTE"
            conversation_history += f"<{role}> {msg.content} </{role}>\n"

        # El prompt completo incluye el historial y la nueva pregunta
        full_prompt = (
            f"Tu tarea es responder al siguiente mensaje basándote en el historial si es relevante.\n"
            f"HISTORIAL: {conversation_history}\n"
            f"PREGUNTA ACTUAL: {current_message}"
        )

        # Aplicar la plantilla de instrucción de Mistral
        return MISTRAL_INSTRUCT_TEMPLATE.format(prompt=full_prompt)

    def query_ai_model(self, current_message: str, history: List[MessageDTO]) -> dict:
        """
        Consulta el modelo de IA real usando verbos canónicos.
        """
        start_time = time.time()
        formatted_prompt = self._format_for_mistral(history, current_message)

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.7
                # Se pueden añadir más parámetros para controlar la generación
            }
        }

        try:
            response = requests.post(self.endpoint_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()

            # Asumiendo que la respuesta es una lista de resultados, tomamos el primero
            raw_response = response.json()[0]['generated_text']

            # Limpiar la respuesta (ya que los modelos a menudo repiten el prompt)
            bot_reply = raw_response.replace(formatted_prompt, "").strip()

        except requests.exceptions.RequestException as e:
            bot_reply = f"Error de conexión con el servicio IA: {e}"
            print(f"Error de API: {e}")
        except Exception as e:
            bot_reply = f"Error al procesar la respuesta de la IA: {e}"
            print(f"Error de procesamiento: {e}")

        end_time = time.time()

        return {
            "text": bot_reply,
            "latency_ms": int((end_time - start_time) * 1000)
        }