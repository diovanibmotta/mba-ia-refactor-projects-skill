import logging
from database import get_db
from src.models import order_model
from src.config.settings import VALID_ORDER_STATUSES

logger = logging.getLogger(__name__)


def list_orders():
    return order_model.get_all()


def list_orders_by_user(usuario_id):
    return order_model.get_by_user(usuario_id)


def create_order(usuario_id, itens):
    if not usuario_id:
        return {"success": False, "error": "usuario_id e obrigatorio"}
    if not itens:
        return {"success": False, "error": "Pedido deve ter pelo menos 1 item"}

    db = get_db()
    cursor = db.cursor()

    total = 0
    validated_items = []

    for item in itens:
        produto = order_model.get_product_for_order(cursor, item["produto_id"])
        if produto is None:
            return {"success": False, "error": f"Produto {item['produto_id']} nao encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"success": False, "error": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]
        validated_items.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco": produto["preco"],
        })

    pedido_id = order_model.create(usuario_id, validated_items, total)
    logger.info("Order created id=%s user=%s total=%.2f", pedido_id, usuario_id, total)
    return {"success": True, "pedido_id": pedido_id, "total": total}


def update_order_status(pedido_id, novo_status):
    if novo_status not in VALID_ORDER_STATUSES:
        return {"success": False, "error": f"Status invalido. Use: {VALID_ORDER_STATUSES}"}

    order_model.update_status(pedido_id, novo_status)
    logger.info("Order status updated id=%s status=%s", pedido_id, novo_status)
    return {"success": True}
