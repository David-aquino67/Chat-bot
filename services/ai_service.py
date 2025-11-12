import time
import requests
from typing import List
from models.message_dto import MessageDTO

TINYLAMA_INSTRUCT_TEMPLATE = "<s>[INST] {prompt} [/INST]"

"""
    Servicio Agnóstico para interactuar con el modelo TinyLlama-1.1B-Chat-v1.0.
    """
class AIService:


    def __init__(self, endpoint_url: str, api_key: str):
        self.endpoint_url = endpoint_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _format_for_mistral(self, history: List[MessageDTO], current_message: str) -> List[dict]:
        messages = [
            {"role": "system", "content": "You are a helpful and expert assistant."}
        ]

        for msg in history:
            role = "user" if msg.sender == 'usuario' else "assistant"
            messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": current_message})

        return messages

    def query_ai_model(self, current_message: str, history: List[MessageDTO]) -> dict:
        start_time = time.time()

        messages = self._format_for_mistral(history, current_message)
        payload = {
            "model": "moonshotai/Kimi-K2-Thinking:novita",
            "messages": messages,
            "max_tokens": 256,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.endpoint_url, headers=self.headers, json=payload, timeout=90)
            response.raise_for_status()
            response_data = response.json()
            if response_data and 'choices' in response_data and response_data['choices']:
                message = response_data['choices'][0].get('message', {})
                raw_response = message.get('content', '')
            else:
                raw_response = ""
                print("ADVERTENCIA: Respuesta de IA exitosa (200 OK), pero contenido 'choices' vacío o nulo.")

            bot_reply = raw_response.strip()

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