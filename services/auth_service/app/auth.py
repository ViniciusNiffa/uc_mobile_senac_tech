from flask import request, jsonify
import jwt, os
from functools import wraps

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: A variável de ambiente SECRET_KEY não foi configurada.")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Token ausente"}), 401
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # As rotas leem daqui (request.user["id"]) em vez de confiar
            # em id que venha no corpo ou na URL.
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        return f(*args, **kwargs)
    return decorated