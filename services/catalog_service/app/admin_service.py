"""
Admin — CRUD de produtos (peças), variações, imagens e upload.
Toda escrita passa por admin_required nas rotas (JWT tipo=admin).
Regras de segurança de dados:
  - SQL sempre parametrizado
  - produtos: soft delete (ativo=0) — são referenciados por favoritos/pedidos
  - variacoes: nunca hard-delete (FK de carrinhos/itens_pedido) — remoção = estoque 0
  - imagens_produto: pode substituir (nada referencia a imagem)
  - upload: whitelist de extensão, secure_filename, sem path traversal
"""
import os
import re
import uuid
import logging
import unicodedata
from werkzeug.utils import secure_filename
from .database import get_connection
from .alerta_service import disparar_alertas_async

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(_h)

TIPOS_VALIDOS = {'moletom', 'calca', 'acessorio', 'camisa', 'tenis', 'jaqueta'}
ALLOWED_EXT = {'.webp', '.jpg', '.jpeg', '.png'}
MAX_UPLOAD = 5 * 1024 * 1024  # 5 MB

# statics/img na raiz do projeto (3 níveis acima de services/catalog_service/app/)
STATIC_IMG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'statics', 'img')
)
UPLOAD_SUBDIR = 'uploads'  # statics/img/uploads/


# ─────────────────────────── helpers ───────────────────────────
def slugify(text):
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
    return text or 'peca'


def _gerar_sku(slug, tamanho):
    base = re.sub(r'[^A-Z0-9]+', '', (slug or 'sku').upper().replace('-', ''))[:40]
    tam = re.sub(r'[^A-Z0-9]+', '', str(tamanho or '').upper())[:6] or 'U'
    return (base + '-' + tam)[:50]


def _slug_unico(cursor, base, exclude_id=None):
    slug, i = base, 2
    while True:
        if exclude_id:
            cursor.execute("SELECT id FROM produtos WHERE slug=%s AND id<>%s", (slug, exclude_id))
        else:
            cursor.execute("SELECT id FROM produtos WHERE slug=%s", (slug,))
        if not cursor.fetchone():
            return slug
        slug = "{}-{}".format(base, i)
        i += 1


def _img_segura(caminho):
    """Aceita só caminhos relativos dentro de statics/img, com extensão permitida."""
    if not caminho or not isinstance(caminho, str):
        return None
    c = caminho.strip().replace('\\', '/').lstrip('/')
    if c.startswith('statics/'):
        c = c[len('statics/'):]
    if '..' in c or not c.startswith('img/'):
        return None
    if os.path.splitext(c)[1].lower() not in ALLOWED_EXT:
        return None
    return c


def _validar(data):
    nome = (data.get('nome') or '').strip()
    if not nome:
        return "Nome é obrigatório."
    if len(nome) > 150:
        return "Nome muito longo (máx. 150 caracteres)."
    try:
        preco = float(data.get('preco_base'))
    except (TypeError, ValueError):
        return "Preço inválido."
    if preco < 0:
        return "Preço não pode ser negativo."
    if (data.get('tipo') or '').strip() not in TIPOS_VALIDOS:
        return "Tipo inválido."
    return None


# ─────────────────────────── leitura ───────────────────────────
def listar_produtos(status='ativas'):
    ativo = 0 if status == 'desativadas' else 1
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.id, p.nome, p.slug, p.preco_base, p.tipo, p.ativo, p.drop_nome, p.is_special,
               i.caminho_imagem AS imagem,
               COALESCE(SUM(v.estoque), 0) AS total_estoque,
               COUNT(DISTINCT v.id) AS num_variacoes
        FROM produtos p
        LEFT JOIN imagens_produto i ON p.id = i.produto_id AND i.ordem_exibicao = 0
        LEFT JOIN variacoes v ON p.id = v.produto_id
        WHERE p.ativo = %s
        GROUP BY p.id
        ORDER BY p.id DESC
    """, (ativo,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def obter_produto(pid):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM produtos WHERE id=%s", (pid,))
    produto = cur.fetchone()
    if not produto:
        cur.close()
        conn.close()
        return None
    cur.execute("SELECT id, tamanho, sku, estoque FROM variacoes WHERE produto_id=%s ORDER BY id", (pid,))
    produto['variacoes'] = cur.fetchall()
    cur.execute("SELECT id, caminho_imagem, ordem_exibicao FROM imagens_produto WHERE produto_id=%s ORDER BY ordem_exibicao", (pid,))
    produto['imagens'] = cur.fetchall()
    cur.close()
    conn.close()
    return produto


# ─────────────────────────── escrita ───────────────────────────
def criar_produto(data):
    err = _validar(data)
    if err:
        return None, err

    nome = data['nome'].strip()
    descricao = (data.get('descricao') or '').strip()
    preco = float(data['preco_base'])
    tipo = data['tipo'].strip()
    is_special = 1 if data.get('is_special') else 0
    drop_nome = (data.get('drop_nome') or '').strip() or None
    imagens = [c for c in (_img_segura(x) for x in (data.get('imagens') or [])) if c]
    variacoes = data.get('variacoes') or []

    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()
    try:
        slug = _slug_unico(cur, slugify(nome))
        cur.execute(
            """INSERT INTO produtos (nome, slug, descricao, preco_base, tipo, ativo, drop_nome, is_special)
               VALUES (%s,%s,%s,%s,%s,1,%s,%s)""",
            (nome, slug, descricao, preco, tipo, drop_nome, is_special)
        )
        pid = cur.lastrowid
        for ordem, cam in enumerate(imagens):
            cur.execute(
                "INSERT INTO imagens_produto (produto_id, caminho_imagem, ordem_exibicao) VALUES (%s,%s,%s)",
                (pid, cam, ordem)
            )
        for v in variacoes:
            tam = str(v.get('tamanho') or '').strip()
            if not tam:
                continue
            est = max(0, int(v.get('estoque') or 0))
            cur.execute(
                "INSERT INTO variacoes (produto_id, tamanho, sku, estoque) VALUES (%s,%s,%s,%s)",
                (pid, tam, _gerar_sku(slug, tam), est)
            )
        conn.commit()
        return pid, None
    except Exception as e:
        conn.rollback()
        logger.error("Erro ao criar peça: %s", e)
        return None, "Não foi possível criar a peça. Verifique os dados e tente de novo."
    finally:
        cur.close()
        conn.close()


def atualizar_produto(pid, data):
    err = _validar(data)
    if err:
        return False, err

    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()
    reabastecidos = []
    try:
        cur.execute("SELECT slug FROM produtos WHERE id=%s", (pid,))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            return False, "Peça não encontrada."
        slug_atual = row[0]

        cur.execute("SELECT id, estoque FROM variacoes WHERE produto_id=%s", (pid,))
        estoque_ant = {r[0]: r[1] for r in cur.fetchall()}

        cur.execute(
            """UPDATE produtos
               SET nome=%s, descricao=%s, preco_base=%s, tipo=%s, is_special=%s, drop_nome=%s, ativo=%s
               WHERE id=%s""",
            (data['nome'].strip(), (data.get('descricao') or '').strip(), float(data['preco_base']),
             data['tipo'].strip(), 1 if data.get('is_special') else 0,
             (data.get('drop_nome') or '').strip() or None,
             0 if data.get('ativo') == 0 or data.get('ativo') is False else 1, pid)
        )

        # Imagens: substitui (nada referencia imagens_produto.id → seguro)
        cur.execute("DELETE FROM imagens_produto WHERE produto_id=%s", (pid,))
        imagens = [c for c in (_img_segura(x) for x in (data.get('imagens') or [])) if c]
        for ordem, cam in enumerate(imagens):
            cur.execute(
                "INSERT INTO imagens_produto (produto_id, caminho_imagem, ordem_exibicao) VALUES (%s,%s,%s)",
                (pid, cam, ordem)
            )

        # Variações: upsert; removidas viram estoque 0 (FK-safe, sem hard-delete)
        ids_mantidos = []
        for v in (data.get('variacoes') or []):
            tam = str(v.get('tamanho') or '').strip()
            if not tam:
                continue
            est = max(0, int(v.get('estoque') or 0))
            vid = v.get('id')
            if vid:
                cur.execute("UPDATE variacoes SET tamanho=%s, estoque=%s WHERE id=%s AND produto_id=%s",
                            (tam, est, int(vid), pid))
                ids_mantidos.append(int(vid))
                if estoque_ant.get(int(vid), -1) == 0 and est > 0:
                    reabastecidos.append(int(vid))
            else:
                cur.execute("INSERT INTO variacoes (produto_id, tamanho, sku, estoque) VALUES (%s,%s,%s,%s)",
                            (pid, tam, _gerar_sku(slug_atual, tam), est))
                ids_mantidos.append(cur.lastrowid)

        cur.execute("SELECT id FROM variacoes WHERE produto_id=%s", (pid,))
        for (ex_id,) in cur.fetchall():
            if ex_id not in ids_mantidos:
                cur.execute("UPDATE variacoes SET estoque=0 WHERE id=%s", (ex_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Erro ao atualizar peça %s: %s", pid, e)
        return False, "Não foi possível atualizar a peça. Verifique os dados e tente de novo."
    finally:
        cur.close()
        conn.close()

    if reabastecidos:
        disparar_alertas_async(pid, reabastecidos)
    return True, None


def desativar_produto(pid):
    """Soft delete — some da loja, preserva histórico/FKs."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE produtos SET ativo=0 WHERE id=%s", (pid,))
    ok = cur.rowcount > 0
    cur.close()
    conn.close()
    return ok


def reativar_produto(pid):
    """Reativa produto (ativo=1) para que volte a aparecer na loja."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE produtos SET ativo=1 WHERE id=%s", (pid,))
    ok = cur.rowcount > 0
    cur.close()
    conn.close()
    return ok


def excluir_produto_hard(pid):
    """Hard delete permanente — bloqueia se houver pedidos associados."""
    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM produtos WHERE id=%s", (pid,))
        if not cur.fetchone():
            return False, "Peça não encontrada."

        # Bloqueia se algum pedido referenciar variações deste produto
        try:
            cur.execute("""
                SELECT COUNT(*) FROM itens_pedido ip
                INNER JOIN variacoes v ON ip.variacao_id = v.id
                WHERE v.produto_id = %s
            """, (pid,))
            (qtd,) = cur.fetchone()
            if qtd > 0:
                return False, "Não é possível excluir: este produto aparece em {} pedido(s). Desative-o para removê-lo da loja.".format(qtd)
        except Exception:
            pass  # tabela em outro banco — prossegue

        cur.execute("DELETE FROM imagens_produto WHERE produto_id=%s", (pid,))
        try:
            cur.execute("DELETE FROM favoritos WHERE produto_id=%s", (pid,))
        except Exception:
            pass
        cur.execute("DELETE FROM variacoes WHERE produto_id=%s", (pid,))
        cur.execute("DELETE FROM produtos WHERE id=%s", (pid,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        logger.error("Erro ao excluir peça %s: %s", pid, e)
        return False, "Não foi possível excluir: verifique se não há pedidos ou itens de carrinho associados."
    finally:
        cur.close()
        conn.close()


def ids_do_drop(drop_nome):
    """IDs das peças que estão num drop (pelo drop_nome)."""
    drop_nome = (drop_nome or '').strip()
    if not drop_nome:
        return []
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM produtos WHERE drop_nome=%s", (drop_nome,))
    ids = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return ids


def atribuir_drop(drop_nome, produto_ids):
    """Sincroniza as peças de um drop: marca as selecionadas com o drop_nome
    e tira o drop_nome das que saíram. Tudo parametrizado."""
    drop_nome = (drop_nome or '').strip()
    if not drop_nome:
        return
    ids = []
    for x in (produto_ids or []):
        try:
            ids.append(int(x))
        except (TypeError, ValueError):
            pass
    conn = get_connection()
    cur = conn.cursor()
    try:
        if ids:
            ph = ','.join(['%s'] * len(ids))
            cur.execute(
                "UPDATE produtos SET drop_nome=NULL WHERE drop_nome=%s AND id NOT IN (" + ph + ")",
                [drop_nome] + ids
            )
            cur.execute(
                "UPDATE produtos SET drop_nome=%s WHERE id IN (" + ph + ")",
                [drop_nome] + ids
            )
        else:
            cur.execute("UPDATE produtos SET drop_nome=NULL WHERE drop_nome=%s", (drop_nome,))
    finally:
        cur.close()
        conn.close()


# ─────────────────────────── upload ───────────────────────────
def salvar_upload(file_storage):
    nome_original = file_storage.filename or ''
    ext = os.path.splitext(nome_original)[1].lower()
    if ext not in ALLOWED_EXT:
        return None, "Formato não permitido. Use webp, jpg ou png."

    # Tamanho (lê o stream sem estourar memória)
    file_storage.stream.seek(0, os.SEEK_END)
    tamanho = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if tamanho == 0:
        return None, "Arquivo vazio."
    if tamanho > MAX_UPLOAD:
        return None, "Arquivo grande demais (máx. 5 MB)."

    base = secure_filename(os.path.splitext(nome_original)[0]) or 'img'
    nome_final = "{}-{}{}".format(base[:40], uuid.uuid4().hex[:8], ext)

    dest_dir = os.path.join(STATIC_IMG_DIR, UPLOAD_SUBDIR)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.abspath(os.path.join(dest_dir, nome_final))

    # Garante que o caminho final fique dentro de statics/img (anti path traversal)
    if not dest_path.startswith(STATIC_IMG_DIR + os.sep):
        return None, "Caminho de destino inválido."

    file_storage.save(dest_path)
    return "img/{}/{}".format(UPLOAD_SUBDIR, nome_final), None
