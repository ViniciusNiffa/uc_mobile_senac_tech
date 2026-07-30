"""
GR!TTA — Alerta de estoque ("Avise-me quando chegar").
Registro de interesse por variação + disparo assíncrono de e-mail após reabastecimento.
"""
import os
import re
import jwt
import logging
import threading
import datetime
import requests

from .database import get_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(_h)

SECRET_KEY       = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: SECRET_KEY não configurada.")
NOTIFICATION_URL = os.environ.get('NOTIFICATION_URL', 'http://127.0.0.1:5007/api/notificar/email')
LOJA_URL         = os.environ.get('LOJA_URL', 'http://127.0.0.1:5599/templates')

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _token_servico():
    payload = {
        'sys': True,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def registrar_alerta(produto_id, variacao_id, email, nome):
    """Registra (ou re-ativa) um alerta de estoque para uma variação específica."""
    if not produto_id:
        return False, 'ID do produto obrigatório.'
    if not variacao_id:
        return False, 'ID da variação obrigatório.'
    if not email or not _EMAIL_RE.match(str(email).strip()):
        return False, 'E-mail inválido.'

    email = email.strip().lower()
    nome  = (nome or '').strip()[:100] or None

    try:
        produto_id  = int(produto_id)
        variacao_id = int(variacao_id)
    except (ValueError, TypeError):
        return False, 'IDs inválidos.'

    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM produtos WHERE id=%s AND ativo=1", (produto_id,))
        if not cursor.fetchone():
            return False, 'Produto não encontrado.'

        cursor.execute(
            "SELECT id FROM variacoes WHERE id=%s AND produto_id=%s",
            (variacao_id, produto_id)
        )
        if not cursor.fetchone():
            return False, 'Variação não encontrada.'

        cursor.execute("""
            INSERT INTO alertas_estoque (produto_id, variacao_id, email, nome, notificado)
            VALUES (%s, %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE
              nome       = IF(VALUES(nome) IS NOT NULL, VALUES(nome), nome),
              notificado = 0
        """, (produto_id, variacao_id, email, nome))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        logger.error('Erro ao registrar alerta de estoque: %s', e)
        return False, 'Erro ao registrar alerta.'
    finally:
        cursor.close()
        conn.close()


def disparar_alertas_async(produto_id, variacao_ids):
    """Dispara alertas em background para as variações que voltaram ao estoque."""
    if not variacao_ids:
        return
    threading.Thread(
        target=_disparar,
        args=(int(produto_id), list(variacao_ids)),
        daemon=True
    ).start()


def _disparar(produto_id, variacao_ids):
    try:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)

        cur.execute("SELECT nome, slug FROM produtos WHERE id=%s", (produto_id,))
        produto = cur.fetchone()
        if not produto:
            cur.close(); conn.close()
            return

        placeholders = ','.join(['%s'] * len(variacao_ids))
        cur.execute(
            f"""SELECT ae.id, ae.email, ae.nome, v.tamanho
                FROM alertas_estoque ae
                JOIN variacoes v ON ae.variacao_id = v.id
                WHERE ae.variacao_id IN ({placeholders}) AND ae.notificado = 0""",
            variacao_ids
        )
        alertas = cur.fetchall()

        if alertas:
            ids = [a['id'] for a in alertas]
            ph2 = ','.join(['%s'] * len(ids))
            cur.execute(
                f"UPDATE alertas_estoque SET notificado = 1 WHERE id IN ({ph2})",
                ids
            )
            conn.commit()

        cur.close()
        conn.close()

        produto_url = f"{LOJA_URL}/usuario/produto.html?slug={produto['slug']}"
        for a in alertas:
            try:
                requests.post(
                    f"{NOTIFICATION_URL}/template",
                    json={
                        'email': a['email'],
                        'tipo':  'alerta_estoque',
                        'dados': {
                            'nome':         a['nome'] or a['email'].split('@')[0],
                            'produto_nome': produto['nome'],
                            'tamanho':      a['tamanho'],
                            'produto_url':  produto_url,
                        },
                    },
                    headers={'Authorization': 'Bearer ' + _token_servico()},
                    timeout=10
                )
                logger.info('Alerta enviado: %s → %s [%s]', a['email'], produto['nome'], a['tamanho'])
            except Exception as e:
                logger.error('Falha ao enviar alerta para %s: %s', a['email'], e)
    except Exception as e:
        logger.error('Erro geral em _disparar alertas: %s', e)
