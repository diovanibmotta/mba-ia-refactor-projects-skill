import logging
from src.models import user_model

logger = logging.getLogger(__name__)


def list_users():
    return user_model.get_all()


def get_user(user_id):
    return user_model.get_by_id(user_id)


def create_user(nome, email, senha, tipo="cliente"):
    if not nome or not email or not senha:
        return {"success": False, "error": "Nome, email e senha sao obrigatorios"}
    if len(senha) < 6:
        return {"success": False, "error": "Senha deve ter pelo menos 6 caracteres"}

    user_id = user_model.create(nome, email, senha, tipo)
    logger.info("User created email=%s", email)
    return {"success": True, "id": user_id}


def login(email, senha):
    if not email or not senha:
        return {"success": False, "error": "Email e senha sao obrigatorios"}

    user = user_model.authenticate(email, senha)
    if user:
        logger.info("Login successful email=%s", email)
        return {"success": True, "user": user}

    logger.warning("Login failed email=%s", email)
    return {"success": False, "error": "Email ou senha invalidos"}
