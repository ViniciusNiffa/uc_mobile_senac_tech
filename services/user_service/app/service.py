from .database import get_connection

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, sobrenome, email, cpf, telefone, tipo FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def update_user(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE usuarios SET nome = %s, telefone = %s WHERE id = %s"
    cursor.execute(query, (data['nome'], data['telefone'], user_id))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success

def get_user_addresses(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM enderecos WHERE usuario_id = %s", (user_id,))
    addresses = cursor.fetchall()
    cursor.close()
    conn.close()
    return addresses

def add_address(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    query = """INSERT INTO enderecos (usuario_id, cep, rua, numero, bairro, cidade, estado) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (user_id, data['cep'], data['rua'], data['numero'], 
                          data['bairro'], data['cidade'], data['estado']))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

def delete_address(user_id, address_id):
    conn = get_connection()
    cursor = conn.cursor()
    # usuario_id no WHERE: o id do endereço sozinho apagaria o de qualquer um
    cursor.execute("DELETE FROM enderecos WHERE id = %s AND usuario_id = %s", (address_id, user_id))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success

def get_user_favorites(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT f.id, f.produto_id, p.nome, p.preco_base as preco, p.slug, i.caminho_imagem as imagem
        FROM favoritos f
        JOIN produtos p ON f.produto_id = p.id
        LEFT JOIN imagens_produto i ON p.id = i.produto_id AND i.ordem_exibicao = 0
        WHERE f.usuario_id = %s
    """
    cursor.execute(query, (user_id,))
    favs = cursor.fetchall()
    cursor.close()
    conn.close()
    return favs

def add_favorite(user_id, produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO favoritos (usuario_id, produto_id) VALUES (%s, %s)", (user_id, produto_id))
        conn.commit()
        return cursor.lastrowid
    except:
        return None
    finally:
        cursor.close()
        conn.close()

def remove_favorite(user_id, fav_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favoritos WHERE id = %s AND usuario_id = %s", (fav_id, user_id))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success