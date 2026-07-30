"""
GR!TTA — Avaliações (reviews) de produtos.
Lista com média/estrelas e cria avaliações (1 por usuário por produto).
"""
import logging
from .database import get_connection

logger = logging.getLogger(__name__)


def listar_avaliacoes(slug):
    """Avaliações de um produto (por slug) + média e total."""
    vazio = {"media": 0, "total": 0, "avaliacoes": []}
    conn = get_connection()
    if not conn:
        return vazio
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM produtos WHERE slug = %s", (slug,))
    prod = cur.fetchone()
    if not prod:
        cur.close()
        conn.close()
        return vazio
    cur.execute("""
        SELECT a.id, a.nota, a.comentario, a.criado_em, u.nome
        FROM avaliacoes a
        JOIN usuarios u ON a.usuario_id = u.id
        WHERE a.produto_id = %s
        ORDER BY a.criado_em DESC
    """, (prod["id"],))
    avs = cur.fetchall()
    cur.close()
    conn.close()

    for a in avs:
        a["criado_em"] = a["criado_em"].isoformat() if a.get("criado_em") else None
        a["nome"] = (a.get("nome") or "Cliente").strip().split(" ")[0]  # só o 1º nome (privacidade)
    total = len(avs)
    media = round(sum(a["nota"] for a in avs) / total, 1) if total else 0
    return {"media": media, "total": total, "avaliacoes": avs}


def criar_avaliacao(produto_id, usuario_id, nota, comentario):
    """Cria/atualiza a avaliação do usuário para o produto (1 por usuário)."""
    try:
        nota = int(nota)
    except (TypeError, ValueError):
        return None, "Nota inválida."
    if nota < 1 or nota > 5:
        return None, "A nota deve ser de 1 a 5 estrelas."
    comentario = (comentario or "").strip()[:1000]

    conn = get_connection()
    if not conn:
        return None, "Erro de conexão com o banco."
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM produtos WHERE id = %s AND ativo = 1", (produto_id,))
        if not cur.fetchone():
            return None, "Produto não encontrado."
        cur.execute(
            "INSERT INTO avaliacoes (produto_id, usuario_id, nota, comentario) VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE nota = VALUES(nota), comentario = VALUES(comentario), criado_em = NOW()",
            (produto_id, usuario_id, nota, comentario))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao criar avaliação: {e}")
        return None, "Não foi possível salvar sua avaliação."
    finally:
        cur.close()
        conn.close()
