from flask import Blueprint, request, jsonify
from src.controllers import user_controller

user_bp = Blueprint("users", __name__)


@user_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = user_controller.list_users()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


@user_bp.route("/usuarios/<int:user_id>", methods=["GET"])
def buscar_usuario(user_id):
    usuario = user_controller.get_user(user_id)
    if not usuario:
        return jsonify({"erro": "Usuario nao encontrado"}), 404
    return jsonify({"dados": usuario, "sucesso": True}), 200


@user_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisicao invalido"}), 400

    result = user_controller.create_user(
        nome=data.get("nome", ""),
        email=data.get("email", ""),
        senha=data.get("senha", ""),
    )
    if not result["success"]:
        return jsonify({"erro": result["error"]}), 400
    return jsonify({"dados": {"id": result["id"]}, "sucesso": True}), 201


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisicao invalido"}), 400

    result = user_controller.login(
        email=data.get("email", ""),
        senha=data.get("senha", ""),
    )
    if not result["success"]:
        return jsonify({"erro": result["error"], "sucesso": False}), 401
    return jsonify({"dados": result["user"], "sucesso": True, "mensagem": "Login OK"}), 200
