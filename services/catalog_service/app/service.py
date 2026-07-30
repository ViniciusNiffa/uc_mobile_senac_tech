from .database import get_connection

ORDENS = {
    'preco_asc': 'p.preco_base ASC',
    'preco_desc': 'p.preco_base DESC',
    'recentes': 'p.criado_em DESC',
    'nome': 'p.nome ASC',
}

def get_all_products(tipo=None, special=None, drop=None, q=None,
                     preco_min=None, preco_max=None, tamanho=None, ordem=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # A query cresce por concatenação conforme os filtros chegam. Os valores vão
    # sempre em params (%s) — nada de f-string com input do usuário aqui.
    query = """
        SELECT p.*, i.caminho_imagem as imagem, i2.caminho_imagem as imagem_2,
               SUM(v.estoque) as total_estoque,
               GROUP_CONCAT(DISTINCT v.tamanho) as tamanhos_disponiveis,
               GROUP_CONCAT(CONCAT(v.id, ':', v.tamanho, ':', v.estoque)) as variacoes
        FROM produtos p
        LEFT JOIN imagens_produto i  ON p.id = i.produto_id  AND i.ordem_exibicao  = 0
        LEFT JOIN imagens_produto i2 ON p.id = i2.produto_id AND i2.ordem_exibicao = 1
        LEFT JOIN variacoes v ON p.id = v.produto_id
        WHERE p.ativo = 1"""
    params = []

    # ?q= — busca só por nome da peça; descrição não entra pra não trazer ruído
    if q:
        termo = q.strip()
        if termo:
            query += " AND p.nome LIKE %s"
            params.append(f"%{termo}%")

    # ?tipo= — a URL usa slug no plural ("camisas"), o banco guarda o ENUM no
    # singular ("camisa"). Esse mapa é a tradução entre os dois.
    if tipo:
        mapping = {
            # slugs antigos, mantidos pra não quebrar link já compartilhado
            'camisas':           'camisa',
            'camisetas':         'camisa',
            'moletons':          'moletom',
            'calcas':            'calca',
            'tenis':             'tenis',
            'acessorios':        'acessorio',
            'casacos':           'jaqueta',
            'jaquetas':          'jaqueta',
            # slugs do menu atual
            'camisa-e-t-shirt':  'camisa',
            'casacos-e-jaqueta': 'jaqueta',
            # quem já mandar o singular passa direto
            'camisa':    'camisa',
            'moletom':   'moletom',
            'calca':     'calca',
            'acessorio': 'acessorio',
        }
        tipo_filtrado = mapping.get(tipo.lower(), tipo)
        query += " AND tipo = %s"
        params.append(tipo_filtrado)

    # ?special=true — só as peças marcadas como destaque (vitrine da home)
    if special == 'true':
        query += " AND is_special = 1"

    # ?drop= — peças de um drop específico, pelo nome gravado em drop_nome
    if drop:
        query += " AND drop_nome = %s"
        params.append(drop)

    # Filtro de preço (?preco_min / ?preco_max)
    if preco_min not in (None, ''):
        try:
            query += " AND p.preco_base >= %s"; params.append(float(preco_min))
        except (TypeError, ValueError):
            pass
    if preco_max not in (None, ''):
        try:
            query += " AND p.preco_base <= %s"; params.append(float(preco_max))
        except (TypeError, ValueError):
            pass

    # ?tamanho= — subquery em vez de filtrar o JOIN, senão o SUM(estoque) lá em
    # cima passaria a contar só o tamanho pedido e o total viria errado.
    if tamanho:
        query += " AND p.id IN (SELECT produto_id FROM variacoes WHERE tamanho = %s AND estoque > 0)"
        params.append(tamanho.strip())

    # GROUP BY só depois de todos os WHERE — se entrar antes, o SQL não compila
    query += " GROUP BY p.id"

    # ?ordem= — só os valores de ORDENS entram na query, nunca o texto cru
    if ordem in ORDENS:
        query += " ORDER BY " + ORDENS[ordem]

    cursor.execute(query, params)
    produtos = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return produtos

def get_product_by_slug(slug):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # As imagens saem por subquery, e não por JOIN, de propósito: juntar
    # imagens_produto e variacoes na mesma query dá produto cartesiano
    # (N fotos x M tamanhos) e o GROUP_CONCAT repete cada foto uma vez por
    # tamanho — 4 fotos viram 24 miniaturas na galeria.
    query = """
        SELECT p.*,
               (SELECT ia.caminho_imagem FROM imagens_produto ia
                 WHERE ia.produto_id = p.id
                 ORDER BY ia.ordem_exibicao LIMIT 1) as imagem,
               (SELECT GROUP_CONCAT(ia.caminho_imagem
                         ORDER BY ia.ordem_exibicao SEPARATOR '|')
                  FROM imagens_produto ia
                 WHERE ia.produto_id = p.id) as todas_imagens,
               GROUP_CONCAT(DISTINCT CONCAT(v.id, ':', v.tamanho, ':', v.estoque)) as variacoes
        FROM produtos p
        LEFT JOIN variacoes v ON p.id = v.produto_id
        WHERE (p.slug = %s OR p.id = %s)
        AND p.ativo = 1
        GROUP BY p.id
        LIMIT 1
    """

    cursor.execute(query, (slug, slug))
    produto = cursor.fetchone()

    cursor.close()
    conn.close()
    return produto

def get_related_products(exclude_id, limit=4):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Sugestões do mesmo tipo da peça aberta, tirando ela própria da lista
    query = """
        SELECT p.*, i.caminho_imagem as imagem 
        FROM produtos p
        LEFT JOIN imagens_produto i ON p.id = i.produto_id AND i.ordem_exibicao = 0
        WHERE p.id != %s 
        AND p.tipo = (SELECT tipo FROM produtos WHERE id = %s)
        AND p.ativo = 1
        LIMIT %s
    """
    
    cursor.execute(query, (exclude_id, exclude_id, limit))
    produtos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return produtos