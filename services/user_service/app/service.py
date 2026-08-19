import sqlite3

from .database import get_connection

def get_user_by_id(perfil_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, sobrenome, telefone, data_nasc, foto_perfil
        FROM perfis
        WHERE id = ?
    """, (perfil_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def create_user_profile(conta_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO perfis (
                id,
                nome,
                sobrenome,
                usuario,
                cpf,
                rg,
                celular,
                data_nasc,
                observacao
            )
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            conta_id,
            data["nome"],
            data["sobrenome"],
            data["usuario"],
            data["cpf"],
            data["rg"],
            data["celular"],
            data["data_nasc"],
            data.get("observacao")

        ))
        cursor.execute(""" 
            INSERT INTO enderecos (
                perfil_id,
                cep,
                estado,
                cidade,
                bairro,
                rua,
                numero,
                complemento
            ) 
            VALUES (?,?,?,?,?,?,?)            
        """, (
            conta_id,
            data.get("cep"),
            data["estado"],
            data["cidade"],
            data["bairro"],
            data["rua"],
            data["numero"],
            data.get("complemento")
        ))

        conn.commit()
        return True
    except sqlite3.IntegrityError as error:
        conn.rollback()
        print(f"Erro ao criar perfil: {error}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def update_user(perfil_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        UPDATE perfis
        SET nome = ?, telefone = ?, atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    """
    cursor.execute(query, (data['nome'], data['telefone'], perfil_id))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


def update_profile_photo(perfil_id, photo_path):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE perfis
            SET foto_perfil = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (photo_path, perfil_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as error:
        if conn:
            conn.rollback()
        print(f"Erro ao atualizar foto: {error}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_user_addresses(perfil_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM enderecos
        WHERE perfil_id = ?
    """, (perfil_id,))
    addresses = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(address) for address in addresses]

def add_address(perfil_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO enderecos (perfil_id, cep, rua, numero, bairro, cidade, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (perfil_id, data['cep'], data['rua'], data['numero'], 
                          data['bairro'], data['cidade'], data['estado']))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

def delete_address(perfil_id, address_id):
    conn = get_connection()
    cursor = conn.cursor()
    # perfil_id no WHERE: o id do endereço sozinho apagaria o de qualquer um
    cursor.execute("""
        DELETE FROM enderecos
        WHERE id = ? AND perfil_id = ?
    """, (address_id, perfil_id))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success

def get_user_favorites(perfil_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT f.id, f.produto_id, p.nome, p.preco_base as preco, p.slug, i.caminho_imagem as imagem
        FROM favoritos f
        JOIN produtos p ON f.produto_id = p.id
        LEFT JOIN imagens_produto i ON p.id = i.produto_id AND i.ordem_exibicao = 0
        WHERE f.perfil_id = ?
    """
    cursor.execute(query, (perfil_id,))
    favs = cursor.fetchall()
    cursor.close()
    conn.close()
    return favs

def add_favorite(perfil_id, produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO favoritos (perfil_id, produto_id)
            VALUES (?, ?)
        """, (perfil_id, produto_id))
        conn.commit()
        return cursor.lastrowid
    except:
        return None
    finally:
        cursor.close()
        conn.close()

def remove_favorite(perfil_id, fav_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM favoritos
        WHERE id = ? AND perfil_id = ?
    """, (fav_id, perfil_id))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success
