# backend/services/auth_middleware.py
from functools import wraps
from flask import request, jsonify
from services.auth_service import AuthService  # reutilizamos el servicio existente

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"ok": False, "error": "Token requerido"}), 401

        try:
            data = AuthService.verify_token(token)
            request.user_id = data.get("user_id")  # 👈 coincide con generate_token
            request.user_email = data.get("email")
        except Exception as e:
            return jsonify({"ok": False, "error": f"Token inválido: {e}"}), 401

        return f(*args, **kwargs)
    return decorated
