"""
GR!TTA — Central de notificações in-app (sininho do header).
Tudo escopado pelo usuário autenticado (sem IDOR).
"""
import logging
from .database import get_connection

logger = logging.getLogger(__name__)


def listar_notificacoes(usuario_id, limite=30):
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, titulo, mensagem, link, lida, criado_em FROM notificacoes "
        "WHERE usuario_id = %s ORDER BY criado_em DESC LIMIT %s",
        (usuario_id, limite))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for r in rows:
        r["criado_em"] = r["criado_em"].isoformat() if r.get("criado_em") else None
        r["lida"] = bool(r["lida"])
    return rows


def contar_nao_lidas(usuario_id):
    conn = get_connection()
    if not conn:
        return 0
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM notificacoes WHERE usuario_id = %s AND lida = 0", (usuario_id,))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def marcar_lida(usuario_id, notif_id):
    conn = get_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("UPDATE notificacoes SET lida = 1 WHERE id = %s AND usuario_id = %s",
                    (notif_id, usuario_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def marcar_todas_lidas(usuario_id):
    conn = get_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("UPDATE notificacoes SET lida = 1 WHERE usuario_id = %s AND lida = 0", (usuario_id,))
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()


def criar_notificacao(usuario_id, titulo, mensagem, link=None):
    """Cria uma notificação. Chamável por qualquer serviço (banco compartilhado)."""
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO notificacoes (usuario_id, titulo, mensagem, link) VALUES (%s, %s, %s, %s)",
            (usuario_id, titulo, mensagem, link))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao criar notificação: {e}")
        return None
    finally:
        cur.close()
        conn.close()
