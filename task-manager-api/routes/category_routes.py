from flask import Blueprint, request, jsonify
from controllers.category_controller import (
    list_categories, create_category, update_category, delete_category
)

category_bp = Blueprint('categories', __name__)


@category_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(list_categories()), 200


@category_bp.route('/categories', methods=['POST'])
def create_category_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    result, error, status = create_category(
        name=data.get('name'),
        description=data.get('description', ''),
        color=data.get('color', '#000000'),
    )
    if error:
        return jsonify({'error': error}), status
    return jsonify(result), status


@category_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category_route(cat_id):
    data = request.get_json()
    result, error, status = update_category(cat_id, data)
    if error:
        return jsonify({'error': error}), status
    return jsonify(result), status


@category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category_route(cat_id):
    _, error, status = delete_category(cat_id)
    if error:
        return jsonify({'error': error}), status
    return jsonify({'message': 'Categoria deletada'}), status
