import logging
from src.models import product_model
from src.config.settings import VALID_CATEGORIES

logger = logging.getLogger(__name__)


def list_products():
    return product_model.get_all()


def get_product(product_id):
    return product_model.get_by_id(product_id)


def create_product(nome, descricao, preco, estoque, categoria):
    if not nome or len(nome) < 2:
        return {"success": False, "error": "Nome deve ter pelo menos 2 caracteres"}
    if len(nome) > 200:
        return {"success": False, "error": "Nome deve ter no maximo 200 caracteres"}
    if preco < 0:
        return {"success": False, "error": "Preco nao pode ser negativo"}
    if estoque < 0:
        return {"success": False, "error": "Estoque nao pode ser negativo"}
    if categoria not in VALID_CATEGORIES:
        return {"success": False, "error": f"Categoria invalida. Use: {VALID_CATEGORIES}"}

    product_id = product_model.create(nome, descricao, preco, estoque, categoria)
    logger.info("Product created id=%s", product_id)
    return {"success": True, "id": product_id}


def update_product(product_id, nome, descricao, preco, estoque, categoria):
    existing = product_model.get_by_id(product_id)
    if not existing:
        return {"success": False, "error": "Produto nao encontrado", "status": 404}
    if not nome or len(nome) < 2:
        return {"success": False, "error": "Nome deve ter pelo menos 2 caracteres"}
    if len(nome) > 200:
        return {"success": False, "error": "Nome deve ter no maximo 200 caracteres"}
    if preco < 0:
        return {"success": False, "error": "Preco nao pode ser negativo"}
    if estoque < 0:
        return {"success": False, "error": "Estoque nao pode ser negativo"}
    if categoria not in VALID_CATEGORIES:
        return {"success": False, "error": f"Categoria invalida. Use: {VALID_CATEGORIES}"}

    product_model.update(product_id, nome, descricao, preco, estoque, categoria)
    return {"success": True}


def delete_product(product_id):
    existing = product_model.get_by_id(product_id)
    if not existing:
        return {"success": False, "error": "Produto nao encontrado", "status": 404}
    product_model.delete(product_id)
    logger.info("Product deleted id=%s", product_id)
    return {"success": True}


def search_products(termo, categoria, preco_min, preco_max):
    return product_model.search(termo, categoria, preco_min, preco_max)
