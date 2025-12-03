document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const messageElement = document.getElementById('message');
    const sessionInfoDiv = document.getElementById('sessionInfo');
    const userIdSpan = document.getElementById('userId');
    const sessionIdSpan = document.getElementById('sessionId');
    const chatButton = document.getElementById('goToChat');

    messageElement.classList.add('hidden');
    messageElement.textContent = '';
    sessionInfoDiv.classList.add('hidden');
    chatButton.disabled = true;

    const LOGIN_URL = 'http://127.0.0.1:5000/login';
    let response;
    let data;

    try {
        response = await fetch(LOGIN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        data = await response.json();

        if (response.ok && data.ok) {
            const sessionId = data.session_id;
            const token = data.token;

            localStorage.setItem('chat_session_id', sessionId);
            localStorage.setItem('user_auth_token', token);

            messageElement.textContent = "Inicio de sesión exitoso. Redirigiendo...";
            messageElement.className = 'success';

            setTimeout(() => {
                window.location.href = 'chat.html';
            }, 500);

        } else {
            const errorMsg = data.error || data.message || 'Error al iniciar sesión. Verifica tus credenciales.';
            messageElement.textContent = errorMsg;
            messageElement.className = 'error';
        }

    } catch (error) {
        console.error('Error de red o servidor:', error);
        messageElement.textContent = 'Error de conexión con el servidor.';
        messageElement.className = 'error';
    }

    messageElement.classList.remove('hidden');
});

document.getElementById('goToChat').addEventListener('click', function() {
    const sessionId = localStorage.getItem('chat_session_id');
    alert(`Redirigiendo a la página de chat... \n¡Usando Session ID: ${sessionId} en cada mensaje!`);
});