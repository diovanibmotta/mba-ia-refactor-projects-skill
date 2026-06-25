from flask import Blueprint, request, jsonify
from src.controllers import order_controller

order_bp = Blueprint("orders", __name__)


@order_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    pedidos = order_controller.list_orders()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@order_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    pedidos = order_controller.list_orders_by_user(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@order_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisicao invalido"}), 400

    result = order_controller.create_order(
        usuario_id=data.get("usuario_id"),
        itens=data.get("itens", []),
    )
    if not result["success"]:
        return jsonify({"erro": result["error"], "sucesso": False}), 400
    return jsonify({"dados": {"pedido_id": result["pedido_id"], "total": result["total"]}, "sucesso": True, "mensagem": "Pedido criado"}), 201


@order_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisicao invalido"}), 400

    result = order_controller.update_order_status(
        pedido_id=pedido_id,
        novo_status=data.get("status", ""),
    )
    if not result["success"]:
        return jsonify({"erro": result["error"]}), 400
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
