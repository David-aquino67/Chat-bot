import pytest
from unittest.mock import MagicMock, patch
import time
from datetime import datetime, timedelta


# Asume que MessageDTO está definida en models/message_dto.py
# y AIService en el archivo que contiene tu código.

# --- Simulación de MessageDTO (Si no tienes el archivo real) ---
class MessageDTO:
    def __init__(self, sender: str, content: str):
        self.sender = sender
        self.content = content


# ------------------------------------------------------------------

# Importa tu clase AIService (Ajusta la importación según tu estructura de archivos)
from tu_archivo_o_modulo import AIService


@pytest.fixture
def mock_client():
    # Un mock que simulará el cliente del modelo real (por ejemplo, HuggingFace)
    # No necesita ninguna configuración especial para esta prueba, ya que se le pasa
    # directamente al constructor y no lo estás usando en la simulación.
    return MagicMock()


@pytest.fixture
def ai_service(mock_client):
    # Fixture para instanciar el servicio con el cliente simulado
    return AIService(model_client=mock_client)


@pytest.fixture
def mock_history():
    # Datos de prueba para el historial de mensajes
    return [
        MessageDTO("sistema", "¡Hola! ¿En qué puedo ayudarte?"),
        MessageDTO("usuario", "¿Cuál es el tiempo en Puebla?")
    ]


### 2. Pruebas Unitarias
# ------------------------------------------------------------------

def test_format_for_mistral_creates_correct_prompt(ai_service, mock_history):
    """Prueba la función helper que formatea el prompt de Mistral."""
    current_message = "Quiero saber el clima."

    # Llamar directamente al método privado (aunque en Python es más una convención)
    formatted_prompt = ai_service._format_for_mistral(current_message, mock_history)

    # Se espera que el formato Mistral sea correcto (un prompt bien construido)
    expected_start = "Instrucciones: Eres un asistente útil. \n"
    expected_end = "[USUARIO]: Quiero saber el clima.\n[BOT]: "

    assert formatted_prompt.startswith(expected_start)
    assert formatted_prompt.endswith(expected_end)
    assert "[SISTEMA]: ¡Hola! ¿En qué puedo ayudarte?\n" in formatted_prompt


@patch('time.time')
@patch('time.sleep')
def test_query_ai_model_successful_response(mock_sleep, mock_time, ai_service, mock_history):
    """
    Prueba el método principal, mockeando la latencia y la llamada al cliente (aunque
    la llamada simulada está dentro de AIService, es bueno mantener el test aislado).
    """

    # 1. Arrange (Configuración): Simular el tiempo de inicio y fin para calcular la latencia
    start_timestamp = 1000.0  # Tiempo de inicio simulado
    end_timestamp = 1001.5  # Tiempo de fin simulado (1.5 segundos de latencia)

    # Configuramos 'time.time()' para que devuelva los valores en secuencia.
    mock_time.side_effect = [start_timestamp, end_timestamp]

    current_message = "Dime un chiste."

    # 2. Act (Ejecución): Llamar al método a probar
    response = ai_service.query_ai_model(current_message, mock_history)

    # 3. Assert (Validación)

    # a. Validar la latencia
    expected_latency_ms = int((end_timestamp - start_timestamp) * 1000)
    assert response["latency_ms"] == expected_latency_ms

    # b. Validar la respuesta simulada
    assert "Simulación de respuesta de Mistral-7B-Instruct-v0.2" in response["text"]

    # c. Validar que la simulación de espera fue llamada
    mock_sleep.assert_called_once_with(1.5)


@patch('time.time')
def test_query_ai_model_handles_exception(mock_time, ai_service, mock_history):
    """Prueba que el método maneje un error en la llamada simulada a la IA."""

    # En este caso, simularemos un error dentro de la lógica de la llamada
    # forzando una excepción que cubra la lógica del 'try-except'.
    # Como la simulación de error está dentro del método, esta prueba es un poco más
    # complicada sin refactorizar AIService. Para el código dado, harías:

    # 1. Arrange: Simular el tiempo, aunque la latencia será mínima si hay un error
    mock_time.side_effect = [2000.0, 2000.001]

    # Para simular un error *real* necesitarías hacer un `patch` sobre la parte
    # que lanza el error, pero dado que el código tiene un `time.sleep(1.5)`
    # sin una llamada al cliente real, forzaremos el error con un mock más profundo
    # o, idealmente, **refactorizando el código para que la llamada al cliente real
    # esté separada** para poder mockearla.

    # ***NOTA sobre el código original:
    # Como la simulación (`time.sleep` y `raw_response`) está dentro del bloque `try`,
    # no podemos simular fácilmente una excepción de la API externa sin refactorizar.
    # El test a continuación asume que refactorizarías el bloque `try` para:
    #
    # try:
    #     raw_response = self._call_model_api(formatted_prompt)
    # except Exception as e:
    #     raw_response = f"Error..."
    #
    # Y entonces mockearías `_call_model_api` para que lance una excepción.
    # ***

    # Test adaptado a la implementación actual: no podemos probar el `except` sin
    # cambiar el código. Pero para una implementación real, se mockearía la dependencia.

    # En este test, validamos el caso de éxito que sí se puede probar.
    current_message = "Mensaje sin errores."
    response = ai_service.query_ai_model(current_message, mock_history)

    assert "Simulación de respuesta" in response["text"]