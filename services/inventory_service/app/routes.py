import logging
import os
from flask import Blueprint, request, jsonify
from .database import get_connection
from .auth import token_required, admin_or_employee_required

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

main = Blueprint('main', __name__)

@main.route('/<int:variacao_id>', methods=['GET'])
def verificar_estoque(variacao_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT estoque, sku, tamanho FROM variacoes WHERE id = %s", (variacao_id,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if item: return jsonify(item), 200
    return jsonify({"error": "Variação não encontrada"}), 404

@main.route('/baixa', methods=['POST'])
@token_required
def dar_baixa():
    # Chamada pelo order_service durante o checkout, nunca pelo navegador.
    data = request.json
    try:
        variacao_id = int(data.get('variacao_id'))
        qtd = int(data.get('quantidade', 1))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "ID ou quantidade inválidos"}), 400

    print(f"[DEBUG] Tentando baixar estoque: ID Variação {variacao_id} | Qtd: {qtd}")

    conn = get_connection()
    cursor = conn.cursor()
    # O "estoque >= %s" no WHERE é o que segura duas compras simultâneas da última
    # peça: quem chegar depois não casa a condição e o rowcount volta 0.
    cursor.execute("UPDATE variacoes SET estoque = estoque - %s WHERE id = %s AND estoque >= %s", (qtd, variacao_id, qtd))
    sucesso = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": sucesso}), 200 if sucesso else 400

@main.route('/devolver', methods=['POST'])
@token_required
def devolver_estoque():
    # Contrapartida da /baixa: o order_service chama aqui quando o checkout
    # aborta depois de já ter reservado peça.
    data = request.json
    variacao_id = data.get('variacao_id')
    qtd = data.get('quantidade', 1)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE variacoes SET estoque = estoque + %s WHERE id = %s", (qtd, variacao_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.warning(f"ESTORNO EXECUTADO: Variação ID {variacao_id} | Quantidade devolvida: {qtd}")
    
    return jsonify({"success": True}), 200

@main.route('/atualizar', methods=['PUT'])
@token_required
@admin_or_employee_required
def atualizar_estoque_manual():
    # Ajuste manual pelo painel: define o saldo, não soma nem subtrai.
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE variacoes SET estoque = %s WHERE id = %s", (data['quantidade'], data['variacao_id']))
    conn.commit()
    return jsonify({"message": "Estoque atualizado manualmente"}), 200