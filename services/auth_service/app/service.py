from .database import get_connection
from .validator import validate_email, validate_password, hash_password, check_password, validate_cpf, validate_phone
from .gmail_service import send_password_reset_email
from sqlite3 import IntegrityError
import hashlib
import jwt
import datetime
import os
import secrets
import logging
import requests
import threading

USER_SERVICE_URL = os.environ.get(
    "USER_SERVICE_URL",
    "http://127.0.0.1:5003/api/users"
)
NOTIFICATION_URL = os.environ.get("NOTIFICATION_URL", "http://127.0.0.1:5007/api/notificar/email")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: A variável de ambiente SECRET_KEY não foi configurada no Auth Service.")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)


def _token_servico():
    """Token curto, assinado com a SECRET_KEY compartilhada, só pra autorizar
    a chamada interna ao notification_service (o reset acontece sem login)."""
    payload = {
        "sys": True,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def _enviar_codigo_email(email, nome, codigo):
    try:
        send_password_reset_email(
            email,
            nome,
            codigo
        )

        logger.info(
            f"E-mail de recuperação enviado para {email}"
        )

    except Exception as error:
        logger.error(
            f"Falha ao enviar código por e-mail: {error}"
        )


def _enviar_template_email(email, tipo, dados):
    """Dispara um e-mail profissional (template) via notification_service, sem bloquear o cadastro."""
    def _task():
        try:
            requests.post(
                NOTIFICATION_URL + "/template",
                json={"email": email, "tipo": tipo, "dados": dados},
                headers={"Authorization": "Bearer " + _token_servico()},
                timeout=10,
            )
        except Exception as e:
            logger.error(f"Falha ao enviar e-mail '{tipo}': {e}")
    threading.Thread(target=_task, daemon=True).start()


def _gerar_otp(usuario_id):
    """Gera OTP de 6 dígitos, invalida os anteriores e persiste o hash."""
    codigo = "{:06d}".format(secrets.randbelow(1000000))
    codigo_hash = hash_password(codigo)
    expiracao = datetime.datetime.now() + datetime.timedelta(minutes=15)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE email_verifications SET usado = 1 WHERE usuario_id = ? AND usado = 0",
            (usuario_id,)
        )
        cursor.execute(
            "INSERT INTO email_verifications (usuario_id, token, expiracao) VALUES (?, ?, ?)",
            (usuario_id, codigo_hash, expiracao)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao gerar OTP de verificação: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    return codigo


def verificar_otp_email(usuario_id, codigo):
    """Valida o OTP de confirmação de e-mail e marca a conta como verificada."""
    if not usuario_id or not codigo:
        return {"message": "ID do usuário e código são obrigatórios."}, 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ev.id, ev.token, ev.tentativas, u.email, u.nome
        FROM email_verifications ev
        JOIN usuarios u ON ev.usuario_id = u.id
        WHERE ev.usuario_id = ? AND ev.usado = 0 AND ev.expiracao > NOW()
        ORDER BY ev.id DESC LIMIT 1
    """, (usuario_id,))
    otp = cursor.fetchone()

    if not otp:
        cursor.close()
        conn.close()
        return {"message": "Código inválido ou expirado. Solicite um novo."}, 400

    if otp['tentativas'] >= 5:
        cursor.execute("UPDATE email_verifications SET usado = 1 WHERE id = ?", (otp['id'],))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Muitas tentativas erradas. Solicite um novo código."}, 429

    if not check_password(str(codigo), otp['token']):
        cursor.execute(
            "UPDATE email_verifications SET tentativas = tentativas + 1 WHERE id = ?",
            (otp['id'],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Código incorreto."}, 400

    email_usuario = otp['email']
    nome_usuario  = otp['nome']
    try:
        cursor.execute("UPDATE email_verifications SET usado = 1 WHERE id = ?", (otp['id'],))
        cursor.execute("UPDATE usuarios SET email_verificado = 1 WHERE id = ?", (usuario_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao confirmar e-mail: {e}")
        cursor.close()
        conn.close()
        return {"message": "Erro ao verificar e-mail."}, 500

    cursor.close()
    conn.close()
    _enviar_template_email(email_usuario, "boas_vindas", {"nome": nome_usuario})
    logger.info(f"E-mail verificado: usuario_id={usuario_id}")
    return {"success": True, "message": "E-mail verificado! Bem-vindo(a) à GR!TTA."}, 200


def reenviar_otp_verificacao(usuario_id):
    """Regenera e reenvia o OTP de verificação de e-mail."""
    if not usuario_id:
        return {"message": "ID do usuário obrigatório."}, 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT email, nome, email_verificado FROM usuarios WHERE id = ? AND ativo = 1",
        (usuario_id,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return {"message": "Usuário não encontrado."}, 404
    if user['email_verificado']:
        return {"message": "E-mail já verificado."}, 400

    try:
        codigo = _gerar_otp(usuario_id)
    except Exception:
        return {"message": "Erro ao gerar código. Tente novamente."}, 500

    _enviar_template_email(user['email'], "verificar_email", {"nome": user['nome'], "codigo": codigo})
    return {"success": True, "message": "Novo código enviado para o seu e-mail."}, 200


def _emitir_tokens(user):
    """Gera access + refresh token pra um usuário (reaproveitado pelo login normal e Google)."""
    access_payload = {
        "id": user["id"], "email": user["email"], "nome": user["nome"], "tipo": user["tipo"],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = secrets.token_urlsafe(64)
    refresh_exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO refresh_tokens (usuario_id, token, expiracao) VALUES (?, ?, ?)",
        (user["id"], refresh_token, refresh_exp)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {
        "success": True, "access_token": access_token, "refresh_token": refresh_token,
        "user_id": user["id"], "tipo": user["tipo"], "message": "Login bem-sucedido"
    }, 200


def login_with_google(token_google):
    """Verifica o ID token do Google no servidor (nunca confia no front),
    acha ou cria o usuário e emite nossos tokens."""
    if not token_google:
        return {"message": "Token do Google ausente."}, 400
    if not GOOGLE_CLIENT_ID:
        return {"message": "Login com Google não está configurado no servidor."}, 503

    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
    except ImportError:
        return {"message": "Biblioteca google-auth não instalada no servidor."}, 503

    try:
        info = google_id_token.verify_oauth2_token(token_google, google_requests.Request(), GOOGLE_CLIENT_ID)
    except Exception as e:
        logger.warning(f"Token Google inválido: {e}")
        return {"message": "Não foi possível validar sua conta Google."}, 401

    if not info.get('email_verified'):
        return {"message": "O e-mail dessa conta Google não está verificado."}, 401

    google_sub = info.get('sub')
    email = info.get('email')
    nome = info.get('name') or (email.split('@')[0] if email else 'Cliente')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, email, tipo, ativo FROM usuarios WHERE google_id = ? OR email = ? LIMIT 1",
        (google_sub, email)
    )
    user = cursor.fetchone()

    try:
        if not user:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, tipo, provider, google_id) VALUES (?, ?, 'cliente', 'google', ?)",
                (nome, email, google_sub)
            )
            conn.commit()
            user = {"id": cursor.lastrowid, "nome": nome, "email": email, "tipo": "cliente"}
            logger.info(f"Novo usuário via Google: {email}")
            _enviar_template_email(email, "boas_vindas", {"nome": nome})   # e-mail de boas-vindas
        elif user.get('ativo') == 0:
            return {"message": "Conta desativada."}, 403
        else:
            # vincula o google_id a uma conta que já existia por e-mail
            cursor.execute("UPDATE usuarios SET google_id = ? WHERE id = ? AND google_id IS NULL", (google_sub, user['id']))
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao criar/vincular conta Google: {e}")
        return {"message": "Erro ao entrar com Google."}, 500
    finally:
        cursor.close()
        conn.close()

    return _emitir_tokens(user)

def register_user(data):
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    cpf = data.get('cpf')
    celular = data.get('celular') # Adicionado para consistência com o frontend

    email_valid, msg = validate_email(email)
    if not email_valid:
        return None, msg
    password_valid, msg = validate_password(senha)
    if not password_valid:
        return None, msg
    cpf_valid, msg = validate_cpf(cpf)
    if not cpf_valid:
        return None, msg
    phone_valid, msg = validate_phone(celular)
    if not phone_valid:
        return None, msg

    conn = get_connection()
    if conn is None:
        return None, "Não foi possível conectar ao banco de dados."
        
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(senha)
        cursor.execute(
            "INSERT INTO contas (email, senha_hash) VALUES (?, ?)",
            (email, hashed_password)
        )
        user_id = cursor.lastrowid
        dados_perfil = {
            "conta_id": user_id,
            "nome": data.get("nome"),
            "sobrenome": data.get("sobrenome"),
            "usuario": data.get("usuario"),
            "cpf": data.get("cpf"),
            "rg": data.get("rg"),
            "celular": data.get("celular"),
            "data_nasc": data.get("data_nasc"),
            "observacao": data.get("observacao"),
            "cep": data.get("cep"),
            "estado": data.get("estado"),
            "cidade": data.get("cidade"),
            "bairro": data.get("bairro"),
            "rua": data.get("rua"),
            "numero": data.get("numero"),
            "complemento": data.get("complemento")
        }

        resposta = requests.post(
            USER_SERVICE_URL,
            json=dados_perfil,
            timeout=5
        )

        if resposta.status_code != 201:
            conn.rollback()
            return None, "A conta não pôde ser criada porque houve um erro ao criar o perfil."

        conn.commit()

        logger.info(f"Novo usuário registrado: {email} (ID: {user_id})")

    except requests.RequestException:
        conn.rollback()
        return None, "O serviço de usuários está indisponível."
    except IntegrityError as e:
        conn.rollback()
        if "email" in str(e):
            return None, "E-mail já cadastrado."
        if "cpf" in str(e):
            return None, "CPF já cadastrado."
        return None, "Erro ao registrar usuário."
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cursor.close()
        conn.close()

    return user_id, None

def login_user(data):
    data = data or {}

    email = data.get("email", "").strip().lower()
    senha = data.get("senha", "")

    if not email or not senha:
        return {"message": "E-mail e senha são obrigatórios."}, 400

    conn = get_connection()

    if conn is None:
        return {"message": "Erro de conexão com o banco de dados."}, 500

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, email, senha_hash, is_admin, ativo
            FROM contas
            WHERE email = ?
        """, (email,))

        user = cursor.fetchone()

        if not user or not check_password(senha, user["senha_hash"]):
            logger.warning(f"Tentativa de login falhou para: {email}")
            return {"message": "E-mail ou senha inválidos."}, 401

        if user["ativo"] == 0:
            return {"message": "Conta desativada."}, 403

        role = "admin" if user["is_admin"] == 1 else "user"

        access_payload = {
            "id": user["id"],
            "email": user["email"],
            "role": role,
            "exp": datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(hours=1)
        }

        access_token = jwt.encode(
            access_payload,
            SECRET_KEY,
            algorithm="HS256"
        )

        refresh_token = secrets.token_urlsafe(64)

        token_hash = hashlib.sha256(
            refresh_token.encode("utf-8")
        ).hexdigest()

        refresh_exp = (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=30)
        ).isoformat()

        cursor.execute("""
            INSERT INTO refresh_tokens (
                conta_id,
                token_hash,
                expira_em
            )
            VALUES (?, ?, ?)
        """, (
            user["id"],
            token_hash,
            refresh_exp
        ))

        conn.commit()

        logger.info(f"Login realizado: {email}")

        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "role": role
            },
            "message": "Login bem-sucedido"
        }, 200

    except Exception as error:
        conn.rollback()
        logger.error(f"Erro durante o login: {error}")
        return {"message": "Erro interno durante o login."}, 500

    finally:
        cursor.close()
        conn.close()

def refresh_access_token(token_cliente):
    if not token_cliente:
        return {"message": "Refresh token não informado."}, 400

    token_hash = hashlib.sha256(
        token_cliente.encode("utf-8")
    ).hexdigest()

    conn = get_connection()

    if conn is None:
        return {"message": "Erro de conexão com o banco de dados."}, 500

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                r.id,
                r.conta_id,
                r.expira_em,
                r.expirado_em,
                c.email,
                c.is_admin,
                c.ativo
            FROM refresh_tokens r
            JOIN contas c ON c.id = r.conta_id
            WHERE r.token_hash = ?
        """, (token_hash,))

        refresh_data = cursor.fetchone()

        if not refresh_data:
            return {
                "message": "Refresh token inválido."
            }, 401

        if refresh_data["expirado_em"] is not None:
            return {
                "message": "Refresh token revogado."
            }, 401

        expira_em = datetime.datetime.fromisoformat(
            refresh_data["expira_em"]
        )

        agora = datetime.datetime.now(datetime.timezone.utc)

        if expira_em <= agora:
            return {
                "message": "Sessão expirada. Faça login novamente."
            }, 401

        if refresh_data["ativo"] == 0:
            return {
                "message": "Conta desativada."
            }, 403

        role = (
            "admin"
            if refresh_data["is_admin"] == 1
            else "user"
        )

        access_payload = {
            "id": refresh_data["conta_id"],
            "email": refresh_data["email"],
            "role": role,
            "exp": agora + datetime.timedelta(hours=1)
        }

        novo_access_token = jwt.encode(
            access_payload,
            SECRET_KEY,
            algorithm="HS256"
        )

        return {
            "success": True,
            "access_token": novo_access_token
        }, 200

    except Exception as error:
        logger.error(f"Erro ao renovar token: {error}")
        return {
            "message": "Erro interno ao renovar token."
        }, 500

    finally:
        cursor.close()
        conn.close()

def logout_user(token_cliente):
    if not token_cliente:
        return {
            "message": "Refresh token não informado."
        }, 400

    token_hash = hashlib.sha256(
        token_cliente.encode("utf-8")
    ).hexdigest()

    conn = get_connection()

    if conn is None:
        return {
            "message": "Erro de conexão com o banco de dados."
        }, 500

    cursor = conn.cursor()

    try:
        agora = datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()

        cursor.execute("""
            UPDATE refresh_tokens
            SET expirado_em = ?
            WHERE token_hash = ?
              AND expirado_em IS NULL
        """, (
            agora,
            token_hash
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Logout realizado com sucesso."
        }, 200

    except Exception as error:
        conn.rollback()
        logger.error(f"Erro durante o logout: {error}")

        return {
            "message": "Erro interno durante o logout."
        }, 500

    finally:
        cursor.close()
        conn.close()

def request_password_reset(email):
    resposta = {
        "success": True,
        "message": "Se o e-mail estiver cadastrado, enviamos um código."
    }

    email = (email or "").strip().lower()

    conn = get_connection()
    if conn is None:
        return resposta, 200

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, email
            FROM contas
            WHERE email = ? AND ativo = 1
        """, (email,))

        conta = cursor.fetchone()

        if not conta:
            return resposta, 200

        codigo = f"{secrets.randbelow(1000000):06d}"
        codigo_hash = hash_password(codigo)

        expira_em = (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=15)
        ).isoformat()

        cursor.execute("""
            UPDATE password_resets
            SET usado = 1
            WHERE conta_id = ? AND usado = 0
        """, (conta["id"],))

        cursor.execute("""
            INSERT INTO password_resets (
                conta_id,
                codigo_hash,
                expira_em
            )
            VALUES (?, ?, ?)
        """, (
            conta["id"],
            codigo_hash,
            expira_em
        ))

        conn.commit()

    except Exception as error:
        conn.rollback()
        logger.error(f"Erro ao gerar código de recuperação: {error}")
        return resposta, 200

    finally:
        cursor.close()
        conn.close()

    _enviar_codigo_email(
        conta["email"],
        "Usuário",
        codigo
    )

    logger.info(f"Código de recuperação gerado para {email}")
    return resposta, 200

def verify_reset_code(email, codigo):
    """Confere o código SEM trocar a senha nem consumi-lo (etapa dedicada do fluxo
    profissional: e-mail → código → nova senha). Conta tentativas contra brute force,
    mas mantém o código válido pro passo final (reset_password)."""
    if not email or not codigo:
        return {"message": "E-mail e código são obrigatórios."}, 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pr.id, pr.token, pr.tentativas
        FROM password_resets pr
        JOIN usuarios u ON pr.usuario_id = u.id
        WHERE u.email = ? AND pr.usado = 0 AND pr.expiracao > NOW()
        ORDER BY pr.id DESC LIMIT 1
    """, (email,))
    reset_data = cursor.fetchone()

    if not reset_data:
        cursor.close()
        conn.close()
        return {"message": "Código inválido ou expirado. Solicite um novo."}, 400

    if reset_data['tentativas'] >= 5:
        cursor.execute("UPDATE password_resets SET usado = 1 WHERE id = ?", (reset_data['id'],))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Muitas tentativas erradas. Solicite um novo código."}, 429

    if not check_password(str(codigo), reset_data['token']):
        cursor.execute("UPDATE password_resets SET tentativas = tentativas + 1 WHERE id = ?", (reset_data['id'],))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Código incorreto."}, 400

    cursor.close()
    conn.close()
    return {"success": True, "message": "Código verificado."}, 200


def reset_password(email, codigo, nova_senha):
    email = (email or "").strip().lower()
    codigo = str(codigo or "").strip()

    if not email or len(codigo) != 6 or not codigo.isdigit():
        return {
            "message": "E-mail e código de 6 dígitos são obrigatórios."
        }, 400

    valid, msg = validate_password(nova_senha)
    if not valid:
        return {"message": msg}, 400

    conn = get_connection()
    if conn is None:
        return {"message": "Erro de conexão com o banco."}, 500

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                pr.id,
                pr.conta_id,
                pr.codigo_hash,
                pr.expira_em,
                pr.tentativas
            FROM password_resets pr
            JOIN contas c ON c.id = pr.conta_id
            WHERE c.email = ?
              AND c.ativo = 1
              AND pr.usado = 0
            ORDER BY pr.id DESC
            LIMIT 1
        """, (email,))

        reset_data = cursor.fetchone()

        if not reset_data:
            return {
                "message": "Código inválido ou expirado."
            }, 400

        if reset_data["tentativas"] >= 5:
            cursor.execute("""
                UPDATE password_resets
                SET usado = 1
                WHERE id = ?
            """, (reset_data["id"],))
            conn.commit()

            return {
                "message": "Muitas tentativas erradas. Solicite outro código."
            }, 429

        expira_em = datetime.datetime.fromisoformat(
            reset_data["expira_em"]
        )

        if expira_em.tzinfo is None:
            expira_em = expira_em.replace(
                tzinfo=datetime.timezone.utc
            )

        agora = datetime.datetime.now(datetime.timezone.utc)

        if expira_em <= agora:
            cursor.execute("""
                UPDATE password_resets
                SET usado = 1
                WHERE id = ?
            """, (reset_data["id"],))
            conn.commit()

            return {
                "message": "Código inválido ou expirado."
            }, 400

        if not check_password(
            codigo,
            reset_data["codigo_hash"]
        ):
            cursor.execute("""
                UPDATE password_resets
                SET tentativas = tentativas + 1
                WHERE id = ?
            """, (reset_data["id"],))
            conn.commit()

            return {"message": "Código incorreto."}, 400

        nova_senha_hash = hash_password(nova_senha)

        cursor.execute("""
            UPDATE contas
            SET senha_hash = ?
            WHERE id = ?
        """, (
            nova_senha_hash,
            reset_data["conta_id"]
        ))

        cursor.execute("""
            UPDATE password_resets
            SET usado = 1
            WHERE id = ?
        """, (reset_data["id"],))

        # Encerra as sessões antigas depois da troca de senha.
        cursor.execute("""
            UPDATE refresh_tokens
            SET expirado_em = ?
            WHERE conta_id = ?
              AND expirado_em IS NULL
        """, (
            agora.isoformat(),
            reset_data["conta_id"]
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Senha atualizada! Já pode entrar com a nova senha."
        }, 200

    except Exception as error:
        conn.rollback()
        logger.error(f"Erro ao atualizar senha: {error}")

        return {
            "message": "Erro ao atualizar senha."
        }, 500

    finally:
        cursor.close()
        conn.close()

def get_account_by_email(email):
    email = email.strip().lower()

    conn = get_connection()

    if conn is None:
        return None

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, email, is_admin, ativo, criado_em
            FROM contas
            WHERE email = ?
        """, (email,))

        account = cursor.fetchone()

        if not account:
            return None

        return {
            "id": account["id"],
            "email": account["email"],
            "role": "admin" if account["is_admin"] == 1 else "user",
            "ativo": bool(account["ativo"]),
            "criado_em": account["criado_em"]
        }

    finally:
        cursor.close()
        conn.close()

def delete_account(account_id, authorization_header):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id
            FROM contas
            WHERE id = ?
        """, (account_id,))

        if not cursor.fetchone():
            return {
                "error": "Conta não encontrada."
            }, 404

    finally:
        cursor.close()
        conn.close()

    try:
        resposta_perfil = requests.delete(
            f"{USER_SERVICE_URL}/{account_id}",
            headers={
                "Authorization": authorization_header
            },
            timeout=5
        )

        if resposta_perfil.status_code not in (200, 404):
            return {
                "error": "Não foi possível excluir o perfil do usuário."
            }, 502

    except requests.RequestException:
        return {
            "error": "O serviço de usuários está indisponível."
        }, 503

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM contas
            WHERE id = ?
        """, (account_id,))

        conn.commit()

        return {
            "message": "Usuário excluído com sucesso."
        }, 200

    except Exception as error:
        conn.rollback()
        return {
            "error": str(error)
        }, 500

    finally:
        cursor.close()
        conn.close()