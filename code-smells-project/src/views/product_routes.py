from flask import Blueprint, request, jsonify
from src.controllers import product_controller

product_bp = Blueprint("products", __name__)


@product_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = product_controller.list_products()
    return jsonify({"dados": produtos, "sucesso": True}), 200


@product_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    resultados = product_controller.search_products(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@product_bp.route("/produtos/<int:product_id>", methods=["GET"])
def buscar_produto(product_id):
    produto = product_controller.get_product(product_id)
    if not produto:
        return jsonify({"erro": "Produto nao encontrado"}), 404
    return jsonify({"dados": produto, "sucesso": True}), 200


@product_bp.route("/produtos", methods=["POST"])
def criar_produto():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisicao invalido"}), 400

    result = product_controller.create_product(
        nome=data.get("nome", ""),
        descricao=data.get("descricao", ""),
        preco=data.get("preco", 0),
        estoque=data.get("estoque", 0),
        categoria=data.get("categoria", "geral"),
    )
    if not result["success"]:
        return jsonify({"erro": result["error"]}), 400
    return jsonify({"dados": {"id": result["id"]}, "sucesso": True, "mensagem": "Produto criado"}), 201


@product_bp.route("/produtos/<int:product_id>", methods=["PUT"])
def atualizar_produto(product_id):
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisicao invalido"}), 400

    result = product_controller.update_product(
        product_id=product_id,
        nome=data.get("nome", ""),
        descricao=data.get("descricao", ""),
        preco=data.get("preco", 0),
        estoque=data.get("estoque", 0),
        categoria=data.get("categoria", "geral"),
    )
    if not result["success"]:
        status = result.get("status", 400)
        return jsonify({"erro": result["error"]}), status
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@product_bp.route("/produtos/<int:product_id>", methods=["DELETE"])
def deletar_produto(product_id):
    result = product_controller.delete_product(product_id)
    if not result["success"]:
        status = result.get("status", 400)
        return jsonify({"erro": result["error"]}), status
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
