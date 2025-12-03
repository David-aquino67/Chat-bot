document.addEventListener('DOMContentLoaded', () => {
    const BASE_URL = 'http://127.0.0.1:5000';
    const chatWindow = document.getElementById('chatWindow');
    const userInput = document.getElementById('userInput');
    const sendMessageButton = document.getElementById('sendMessage');
    const sessionDisplay = document.getElementById('currentSessionId');

    const sessionId = localStorage.getItem('chat_session_id');
    const token = localStorage.getItem('user_auth_token');

    if (!sessionId || !token) {
        window.location.href = 'index.html';
        return;
    }
    sessionDisplay.textContent = sessionId;
    loadHistory();
    function displayMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'usuario' ? 'user-message' : 'bot-message');
        const time = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `<span class="content">${content}</span><span class="timestamp">${time}</span>`;
        chatWindow.appendChild(messageDiv);

        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    async function loadHistory() {
        const HISTORY_URL = `${BASE_URL}/mensajes/${sessionId}`;

        try {
            const response = await fetch(HISTORY_URL, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.ok && data.mensajes) {
                    chatWindow.innerHTML = '';
                    data.mensajes.forEach(msg => {
                        displayMessage(msg.remitente, msg.contenido);
                    });
                } else {
                    displayMessage('sistema', '¡Hola! Empieza a chatear. No hay historial.');
                }
            } else {
                console.error("Error al cargar historial:", response.status);
                displayMessage('sistema', `Error ${response.status} al cargar historial.`);
            }
        } catch (error) {
            console.error('Error de red al cargar historial:', error);
            displayMessage('sistema', 'Error de conexión con el servidor. Revisar consola.');
        }
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        displayMessage('usuario', message);
        userInput.value = '';
        sendMessageButton.disabled = true;
        const CHAT_URL = `${BASE_URL}/api/chat`;

        try {
            const response = await fetch(CHAT_URL, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: message
                })
            });

            if (response.ok) {
                const data = await response.json();

                if (data.ok && data.data && data.data.reply) {
                    displayMessage('bot', data.data.reply);
                } else {
                    displayMessage('bot', 'Error: No se recibió respuesta válida del bot.',);
                }
            } else {
                const errorData = await response.json();
                displayMessage('sistema', `Error ${response.status}: ${errorData.error || errorData.message}`, 'Ahora');
            }

        } catch (error) {
            console.error('Error de red al enviar mensaje:', error);
            displayMessage('sistema', 'Error de red. Verifica la conexión.');
        } finally {
            sendMessageButton.disabled = false;
            userInput.focus();
        }
    }
    sendMessageButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

});