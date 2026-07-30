from flask import Blueprint, request, jsonify
import hashlib
import os
from .service import get_all_products, get_product_by_slug, get_related_products
from .storefront import (
    get_estado, list_drops, set_estado,
    ler_drop, salvar_drop, excluir_drop,
    get_categorias, set_categoria
)
from .auth import admin_required, token_required
from .admin_service import (
    listar_produtos, obter_produto, criar_produto,
    atualizar_produto, desativar_produto, reativar_produto,
    excluir_produto_hard, salvar_upload,
    atribuir_drop, ids_do_drop
)

# Segunda confirmação pra exclusão permanente de peça, além do JWT de admin.
# Vem do .env do catalog_service: ADMIN_DELETE_SECRET=...
ADMIN_DELETE_SECRET = os.getenv('ADMIN_DELETE_SECRET', '')
from .avaliacao_service import listar_avaliacoes, criar_avaliacao
from .alerta_service import registrar_alerta

main = Blueprint('main', __name__)

@main.route('/products', methods=['GET'])
def list_products():
    # Todos os filtros são opcionais e se acumulam. Quem monta o SQL é o service;
    # aqui a rota só repassa o que veio na query string.
    produtos = get_all_products(
        tipo=request.args.get('tipo'),
        special=request.args.get('special'),
        drop=request.args.get('drop'),
        q=request.args.get('q'),
        preco_min=request.args.get('preco_min'),
        preco_max=request.args.get('preco_max'),
        tamanho=request.args.get('tamanho'),
        ordem=request.args.get('ordem'),
    )
    return jsonify(produtos), 200

@main.route('/products/<string:slug>', methods=['GET'])
def get_product(slug):
    produto = get_product_by_slug(slug)
    if produto:
        return jsonify(produto), 200
    return jsonify({"error": "Produto não encontrado"}), 404

@main.route('/products/<int:product_id>/related', methods=['GET'])
def get_related(product_id):
    limit = request.args.get('limit', 4, type=int)
    produtos = get_related_products(product_id, limit)
    return jsonify(produtos), 200


# ─────────────────────────────────────────────
#  AVALIAÇÕES (reviews) de produtos
# ─────────────────────────────────────────────
@main.route('/products/<string:slug>/avaliacoes', methods=['GET'])
def get_avaliacoes(slug):
    """Público: lista as avaliações de um produto + média e total."""
    return jsonify(listar_avaliacoes(slug)), 200


@main.route('/products/<int:product_id>/avaliacoes', methods=['POST'])
@token_required
def post_avaliacao(product_id):
    """Cliente logado: cria/atualiza sua avaliação (1 por produto)."""
    data = request.get_json(silent=True) or {}
    ok, err = criar_avaliacao(product_id, request.user.get('id'),
                              data.get('nota'), data.get('comentario'))
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"success": True}), 201


# ─────────────────────────────────────────────
#  DROPS — listagem pública + info + senha
# ─────────────────────────────────────────────
@main.route('/drops', methods=['GET'])
def listar_drops_publico():
    """Público: lista todos os drops (sem senha_hash), com flag ativo/arquivado."""
    estado = get_estado()
    ativo_id = estado.get('ativo')
    resultado = []
    for item in list_drops():
        drop_id = item.get('id')
        if drop_id == 'normal':
            continue
        config = ler_drop(drop_id)
        if not config:
            continue
        thumb = (config.get('thumb')
                 or config.get('drop_page', {}).get('banner', '')
                 or config.get('hero', {}).get('banner', ''))
        resultado.append({
            'id':        config.get('id'),
            'nome':      config.get('nome', ''),
            'drop_nome': config.get('drop_nome'),
            'trancado':  bool(config.get('trancado', False)),
            'arquivado': bool(config.get('arquivado', False)),
            'thumb':     thumb,
            'desc':      config.get('desc', ''),
            'ativo':     drop_id == ativo_id,
        })
    return jsonify(resultado), 200


@main.route('/drops/<string:drop_id>/info', methods=['GET'])
def drop_info(drop_id):
    """Público: retorna metadados do drop (sem expor senha_hash)."""
    config = ler_drop(drop_id)
    if config is None:
        return jsonify({"error": "Drop não encontrado"}), 404
    return jsonify({
        "id":        config.get('id'),
        "nome":      config.get('nome'),
        "drop_nome": config.get('drop_nome'),
        "trancado":  bool(config.get('trancado')),
    }), 200


@main.route('/drops/<string:drop_id>/acesso', methods=['POST'])
def drop_acesso(drop_id):
    """Público: valida a senha de um drop trancado."""
    config = ler_drop(drop_id)
    if config is None:
        return jsonify({"ok": False, "erro": "Drop não encontrado."}), 404
    if not config.get('trancado'):
        return jsonify({"ok": True}), 200
    data  = request.get_json(silent=True) or {}
    senha = (data.get('senha') or '').strip()
    if not senha:
        return jsonify({"ok": False, "erro": "Senha obrigatória."}), 400
    hash_stored   = config.get('senha_hash', '')
    hash_enviado  = hashlib.sha256(senha.encode('utf-8')).hexdigest()
    if hash_enviado != hash_stored:
        return jsonify({"ok": False, "erro": "SENHA INCORRETA."}), 401
    return jsonify({"ok": True}), 200


# ─────────────────────────────────────────────
#  STOREFRONT — estado da loja / drops ativos
# ─────────────────────────────────────────────
@main.route('/storefront', methods=['GET'])
def storefront_get():
    """Público: o front lê o estado ativo e aplica as personalizações."""
    return jsonify(get_estado()), 200


@main.route('/storefront/drops', methods=['GET'])
@admin_required
def storefront_list():
    """Admin: lista os drops/configs disponíveis."""
    return jsonify(list_drops()), 200


@main.route('/storefront/drops/<drop_id>', methods=['GET'])
@admin_required
def storefront_drop_get(drop_id):
    """Admin: carrega a config de um drop + quais peças estão nele (para editar)."""
    config = ler_drop(drop_id)
    if config is None:
        return jsonify({"error": "Drop não encontrado"}), 404
    return jsonify({"config": config, "produto_ids": ids_do_drop(config.get('drop_nome'))}), 200


@main.route('/storefront/drops', methods=['POST'])
@admin_required
def storefront_drop_save():
    """Admin: grava drops/<id>.json e atribui as peças selecionadas ao drop."""
    body = request.get_json(silent=True) or {}
    config = body.get('config') or {}
    drop_id, err = salvar_drop(config)
    if err:
        return jsonify({"error": err}), 400
    # Atribuição de peças depende do MySQL; se falhar, o drop já foi salvo
    try:
        atribuir_drop(config.get('drop_nome'), body.get('produto_ids') or [])
    except Exception as e:
        return jsonify({"success": True, "id": drop_id,
                        "aviso": "Drop salvo, mas falhou ao atribuir peças: {}".format(e)}), 200
    return jsonify({"success": True, "id": drop_id}), 201


@main.route('/storefront/drops/<drop_id>', methods=['DELETE'])
@admin_required
def storefront_drop_delete(drop_id):
    """Admin: exclui um drop (bloqueia 'normal' e o drop ativo)."""
    ok, err = excluir_drop(drop_id)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"success": True}), 200


@main.route('/storefront', methods=['PUT'])
@admin_required
def storefront_set():
    """Admin: define o drop ativo (ou 'normal'). Grava em drops/_estado.json."""
    data = request.get_json(silent=True) or {}
    estado, err = set_estado(data.get('ativo'))
    if err:
        return jsonify({"error": err}), 400
    return jsonify(estado), 200


# ─────────────────────────────────────────────
#  ADMIN — CRUD de peças (tudo protegido)
# ─────────────────────────────────────────────
@main.route('/admin/produtos', methods=['GET'])
@admin_required
def admin_listar():
    status = request.args.get('status', 'ativas')
    return jsonify(listar_produtos(status)), 200


@main.route('/admin/produtos/<int:pid>', methods=['GET'])
@admin_required
def admin_obter(pid):
    produto = obter_produto(pid)
    if not produto:
        return jsonify({"error": "Peça não encontrada"}), 404
    return jsonify(produto), 200


@main.route('/admin/produtos', methods=['POST'])
@admin_required
def admin_criar():
    pid, err = criar_produto(request.get_json(silent=True) or {})
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"success": True, "id": pid}), 201


@main.route('/admin/produtos/<int:pid>', methods=['PUT'])
@admin_required
def admin_atualizar(pid):
    ok, err = atualizar_produto(pid, request.get_json(silent=True) or {})
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"success": True}), 200


@main.route('/admin/produtos/<int:pid>', methods=['DELETE'])
@admin_required
def admin_desativar(pid):
    if not desativar_produto(pid):
        return jsonify({"error": "Peça não encontrada"}), 404
    return jsonify({"success": True}), 200


@main.route('/admin/produtos/<int:pid>/reativar', methods=['PUT'])
@admin_required
def admin_reativar(pid):
    if not reativar_produto(pid):
        return jsonify({"error": "Peça não encontrada"}), 404
    return jsonify({"success": True}), 200


@main.route('/admin/produtos/<int:pid>/excluir', methods=['DELETE'])
@admin_required
def admin_excluir(pid):
    if not ADMIN_DELETE_SECRET:
        return jsonify({"error": "Senha de exclusão não configurada no servidor. Defina ADMIN_DELETE_SECRET no arquivo .env."}), 503
    data = request.get_json(silent=True) or {}
    senha = (data.get('senha') or '').strip()
    if senha != ADMIN_DELETE_SECRET:
        return jsonify({"error": "Senha incorreta."}), 403
    ok, err = excluir_produto_hard(pid)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"success": True}), 200


@main.route('/categories', methods=['GET'])
def get_categories_public():
    """Público: retorna os caminhos de imagem de cada categoria da home."""
    return jsonify(get_categorias()), 200


@main.route('/admin/categories/<string:tipo>', methods=['PUT'])
@admin_required
def admin_set_category(tipo):
    """Admin: atualiza a imagem de uma categoria (grava em drops/_categorias.json)."""
    data = request.get_json(silent=True) or {}
    cats, err = set_categoria(tipo, data.get('caminho', ''))
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"success": True, "categorias": cats}), 200


@main.route('/alertas-estoque', methods=['POST'])
def criar_alerta():
    """Público: registra alerta de reabastecimento para uma variação esgotada."""
    data = request.get_json(silent=True) or {}
    ok, err = registrar_alerta(
        data.get('produto_id'),
        data.get('variacao_id'),
        data.get('email'),
        data.get('nome'),
    )
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'success': True, 'message': 'Você será avisado quando a peça voltar ao estoque!'}), 201


@main.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload():
    arquivo = request.files.get('file')
    if not arquivo:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    caminho, err = salvar_upload(arquivo)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"success": True, "caminho": caminho}), 201