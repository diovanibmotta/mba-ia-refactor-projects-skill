from flask import Blueprint, request, jsonify
from controllers.user_controller import (
    list_users, get_user, create_user, update_user, delete_user,
    get_user_tasks, login
)

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(list_users()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_route(user_id):
    data, error, status = get_user(user_id)
    if error:
        return jsonify({'error': error}), status
    return jsonify(data), status


@user_bp.route('/users', methods=['POST'])
def create_user_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    result, error, status = create_user(
        name=data.get('name'),
        email=data.get('email'),
        password=data.get('password'),
        role=data.get('role', 'user'),
    )
    if error:
        return jsonify({'error': error}), status
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user_route(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    result, error, status = update_user(user_id, data)
    if error:
        return jsonify({'error': error}), status
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    _, error, status = delete_user(user_id)
    if error:
        return jsonify({'error': error}), status
    return jsonify({'message': 'Usuário deletado com sucesso'}), status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks_route(user_id):
    tasks, error, status = get_user_tasks(user_id)
    if error:
        return jsonify({'error': error}), status
    return jsonify(tasks), status


@user_bp.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    user_data, error, status = login(
        email=data.get('email'),
        password=data.get('password'),
    )
    if error:
        return jsonify({'error': error}), status
    return jsonify({'message': 'Login realizado com sucesso', 'user': user_data}), status
