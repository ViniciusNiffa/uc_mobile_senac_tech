from flask import request, jsonify
import jwt, os
from functools import wraps

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: SECRET_KEY não configurada.")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        partes = auth_header.split()

        if len(partes) != 2 or partes[0].lower() != "bearer":
            return jsonify({
                "error": "Token ausente ou cabeçalho inválido"
            }), 401

        token = partes[1]

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=["HS256"]
            )
            request.user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated