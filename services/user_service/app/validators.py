import re
import bcrypt

def validate_email(email):
    if not email:
        return False, "Email é obrigatório"
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Email inválido"
    return True, ""

def validate_password(password):
    if not password:
        return False, "Senha é obrigatória"
    if len(password) < 6:
        return False, "Senha deve ter ao menos 6 caracteres"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Senha deve conter letras e números"
    return True, ""

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def validate_cpf(cpf):
    if not cpf:
        return False, "CPF é obrigatório."
    cpf_clean = re.sub(r'\D', '', cpf)
    if not re.match(r"^\d{11}$", cpf_clean):
        return False, "CPF inválido. Deve conter 11 números."
    return True, ""

def validate_phone(phone):
    if not phone:
        return False, "Telefone é obrigatório"
    # Aceita (XX) XXXXX-XXXX ou apenas números (10 ou 11 dígitos)
    cleaned = re.sub(r'\D', '', phone)
    if len(cleaned) < 10 or len(cleaned) > 11:
        return False, "Telefone inválido. Deve conter DDD e número."
    return True, ""