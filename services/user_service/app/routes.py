from flask import ( Blueprint, request, jsonify, send_from_directory )
from .service import (create_user_profile, get_user_by_id, update_user, get_user_addresses, add_address,
                     delete_address, get_user_favorites, add_favorite, remove_favorite, get_all_users, delete_user_profile, update_profile_photo)
from .notificacao_service import (listar_notificacoes, contar_nao_lidas,
                                  marcar_lida, marcar_todas_lidas)
from .auth import token_required
from pathlib import Path
from uuid import uuid4


main = Blueprint('main', __name__)

UPLOAD_DIR = (
    Path(__file__).resolve().parent.parent
    / "uploads"
)

EXTENSOES_PERMITIDAS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

def _eh_dono(user_id):
    return (
        user_id == request.user.get("id")
        or request.user.get("role") == "admin"
    )

@main.route('/users', methods=['GET'])
@token_required
def list_users():
    if request.user.get("role") != "admin":
        return jsonify({"error": "Acesso permitido somente para administradores"}), 403

    return jsonify(get_all_users()), 200

@main.route('/users', methods=['POST'])
def create_profile():
    data = request.get_json() or {}
    conta_id = data.get("conta_id")

    if not conta_id:
        return jsonify({"error": "conta_id é obrigatório"}), 400
    
    if create_user_profile(conta_id, data):
        return jsonify({
            "success": True,
            "id": conta_id
        }), 201
    
    return jsonify({
        "error": "Não foi possível criar o perfil"
    }), 400


@main.route('/users/<int:user_id>', methods=['GET'])
@token_required
def profile(user_id):
    if not _eh_dono(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    user = get_user_by_id(user_id)
    return jsonify(user) if user else (jsonify({"error": "User not found"}), 404)

@main.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_profile(user_id):
    if not _eh_dono(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    data = request.get_json() or {}
    if update_user(user_id, data):
        return jsonify({"message": "Perfil atualizado"}), 200
    return jsonify({"error": "Falha ao atualizar"}), 400

@main.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_profile(user_id):
    usuario_logado = request.user

    if usuario_logado.get("role") != "admin":
        return jsonify({
            "error": "Apenas administradores podem excluir usuários."
        }), 403

    if usuario_logado.get("id") == user_id:
        return jsonify({
            "error": "O administrador não pode excluir a própria conta."
        }), 400

    if delete_user_profile(user_id):
        return jsonify({
            "message": "Perfil excluído com sucesso."
        }), 200

    return jsonify({
        "error": "Perfil não encontrado."
    }), 404

@main.route('/users/<int:user_id>/addresses', methods=['GET'])
@token_required
def list_addresses(user_id):
    if not _eh_dono(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    return jsonify(get_user_addresses(user_id)), 200

@main.route('/users/<int:user_id>/addresses', methods=['POST'])
@token_required
def create_address(user_id):
    if not _eh_dono(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    data = request.json
    addr_id = add_address(user_id, data)
    return jsonify({"id": addr_id}), 201

@main.route('/users/<int:user_id>/addresses/<int:address_id>', methods=['DELETE'])
@token_required
def remove_address(user_id, address_id):
    if not _eh_dono(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    if delete_address(user_id, address_id):
        return jsonify({"message": "Endereço removido"}), 200
    return jsonify({"error": "Falha ao remover"}), 400

@main.route('/favoritos', methods=['GET'])
@token_required
def list_favs():
    user_id = request.user.get('id')
    return jsonify(get_user_favorites(user_id)), 200

@main.route('/favoritos', methods=['POST'])
@token_required
def create_fav():
    user_id = request.user.get('id')
    data = request.json
    fav_id = add_favorite(user_id, data.get('produto_id'))
    if fav_id:
        return jsonify({"id": fav_id}), 201
    return jsonify({"error": "Erro ao favoritar"}), 400

@main.route('/favoritos/<int:fav_id>', methods=['DELETE'])
@token_required
def delete_fav(fav_id):
    user_id = request.user.get('id')
    if remove_favorite(user_id, fav_id):
        return jsonify({"message": "Removido"}), 200
    return jsonify({"error": "Erro ao remover"}), 400


# ─────────────────────────────────────────────
#  NOTIFICAÇÕES (central in-app / sininho)
# ─────────────────────────────────────────────
@main.route('/notificacoes', methods=['GET'])
@token_required
def list_notifs():
    return jsonify(listar_notificacoes(request.user.get('id'))), 200

@main.route('/notificacoes/count', methods=['GET'])
@token_required
def count_notifs():
    return jsonify({"nao_lidas": contar_nao_lidas(request.user.get('id'))}), 200

@main.route('/notificacoes/<int:notif_id>/lida', methods=['PUT'])
@token_required
def read_notif(notif_id):
    marcar_lida(request.user.get('id'), notif_id)
    return jsonify({"success": True}), 200

@main.route('/notificacoes/lidas', methods=['PUT'])
@token_required
def read_all_notifs():
    marcar_todas_lidas(request.user.get('id'))
    return jsonify({"success": True}), 200

@main.route(
    '/users/<int:user_id>/photo',
    methods=['POST']
)
@token_required
def upload_profile_photo(user_id):
    if not _eh_dono(user_id):
        return jsonify({
            "error": "Acesso negado."
        }), 403

    arquivo = request.files.get("foto")

    if not arquivo or not arquivo.filename:
        return jsonify({
            "error": "Nenhuma foto foi enviada."
        }), 400

    extensao = Path(arquivo.filename).suffix.lower()

    if extensao not in EXTENSOES_PERMITIDAS:
        return jsonify({
            "error": "Use uma imagem JPG, PNG ou WEBP."
        }), 400

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    nome_arquivo = (
        f"perfil_{user_id}_{uuid4().hex}"
        f"{extensao}"
    )

    caminho = UPLOAD_DIR / nome_arquivo
    arquivo.save(caminho)

    if not update_profile_photo(
        user_id,
        nome_arquivo
    ):
        caminho.unlink(missing_ok=True)

        return jsonify({
            "error": "Não foi possível salvar a foto."
        }), 500

    foto_url = (
        f"{request.host_url.rstrip('/')}"
        f"/api/uploads/{nome_arquivo}"
    )

    return jsonify({
        "message": "Foto atualizada com sucesso.",
        "foto_perfil": nome_arquivo,
        "foto_url": foto_url
    }), 200


@main.route(
    '/uploads/<path:nome_arquivo>',
    methods=['GET']
)
def serve_profile_photo(nome_arquivo):
    return send_from_directory(
        UPLOAD_DIR,
        nome_arquivo
    )