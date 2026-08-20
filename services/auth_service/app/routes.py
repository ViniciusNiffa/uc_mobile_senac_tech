import time
from functools import wraps
from collections import defaultdict
from flask import Blueprint, request, jsonify
from .service import (register_user, login_user, logout_user, refresh_access_token,
                      request_password_reset, verify_reset_code, reset_password,
                      login_with_google, verificar_otp_email, reenviar_otp_verificacao, get_account_by_email)
from .auth import token_required

main = Blueprint('main', __name__)

# Rate limiting simples em memória (por IP + endpoint). Reseta no restart —
# suficiente pra travar brute force sem dependência externa.
_tentativas = defaultdict(list)

def rate_limit(max_calls=8, window=60):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = (request.headers.get('X-Forwarded-For', request.remote_addr or 'desconhecido')
                  .split(',')[0].strip())
            agora = time.time()
            chave = (f.__name__, ip)
            recentes = [t for t in _tentativas[chave] if agora - t < window]
            if len(recentes) >= max_calls:
                return jsonify({"message": "Muitas tentativas. Espere um pouco e tente de novo."}), 429
            recentes.append(agora)
            _tentativas[chave] = recentes
            return f(*args, **kwargs)
        return wrapper
    return decorator

@main.route('/register', methods=['POST'])
@rate_limit(max_calls=5, window=60)
def register():
    data = request.json
    user_id, error = register_user(data)
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "Usuário registrado!", "id": user_id}), 201

@main.route('/login', methods=['POST'])
@rate_limit(max_calls=8, window=60)
def login():
    data = request.json
    response, status = login_user(data)
    return jsonify(response), status

@main.route('/google', methods=['POST'])
@rate_limit(max_calls=15, window=60)
def google_login():
    data = request.json or {}
    response, status = login_with_google(data.get('credential') or data.get('id_token'))
    return jsonify(response), status

@main.route('/refresh', methods=['POST'])
@rate_limit(max_calls=20, window=60)
def refresh():
    data = request.get_json() or {}
    token = data.get('refresh_token')
    response, status = refresh_access_token(token)
    return jsonify(response), status

@main.route("/logout", methods=["POST"])
@rate_limit(max_calls=20, window=60)
def logout():
    data = request.get_json() or {}
    token = data.get("refresh_token")

    response, status = logout_user(token)

    return jsonify(response), status

@main.route('/forgot-password', methods=['POST'])
@rate_limit(max_calls=5, window=300)
def forgot():
    email = request.json.get('email')
    response, status = request_password_reset(email)
    return jsonify(response), status

@main.route('/verify-reset-code', methods=['POST'])
@rate_limit(max_calls=10, window=300)
def verify_code():
    data = request.json or {}
    response, status = verify_reset_code(data.get('email'), data.get('codigo'))
    return jsonify(response), status

@main.route('/reset-password', methods=['POST'])
@rate_limit(max_calls=10, window=300)
def reset():
    data = request.json
    response, status = reset_password(data.get('email'), data.get('codigo'), data.get('senha'))
    return jsonify(response), status

@main.route('/verify-email', methods=['POST'])
@rate_limit(max_calls=10, window=300)
def verify_email():
    data = request.json or {}
    response, status = verificar_otp_email(data.get('usuario_id'), data.get('codigo'))
    return jsonify(response), status

@main.route('/resend-otp', methods=['POST'])
@rate_limit(max_calls=3, window=300)
def resend_otp():
    data = request.json or {}
    response, status = reenviar_otp_verificacao(data.get('usuario_id'))
    return jsonify(response), status

@main.route("/accounts/search", methods=["GET"])
@token_required
def search_account():
    email = request.args.get("email", "").strip().lower()

    if not email:
        return jsonify({
            "error": "Email é obrigatório."
        }), 400

    usuario_logado = request.user

    if (
        usuario_logado.get("role") != "admin"
        and usuario_logado.get("email", "").lower() != email
    ):
        return jsonify({
            "error": "Acesso negado."
        }), 403

    account = get_account_by_email(email)

    if not account:
        return jsonify({
            "error": "Conta não encontrada."
        }), 404

    return jsonify(account), 200