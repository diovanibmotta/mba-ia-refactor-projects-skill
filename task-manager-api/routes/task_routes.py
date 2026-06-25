from flask import Blueprint, request, jsonify
from controllers.task_controller import (
    list_tasks, get_task, create_task, update_task, delete_task,
    search_tasks, task_stats
)
from config.settings import DEFAULT_PRIORITY

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(list_tasks()), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def get_stats():
    return jsonify(task_stats()), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search():
    return jsonify(search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_route(task_id):
    data, error, status = get_task(task_id)
    if error:
        return jsonify({'error': error}), status
    return jsonify(data), status


@task_bp.route('/tasks', methods=['POST'])
def create_task_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    result, error, status = create_task(
        title=data.get('title', ''),
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', DEFAULT_PRIORITY),
        user_id=data.get('user_id'),
        category_id=data.get('category_id'),
        due_date=data.get('due_date'),
        tags=data.get('tags'),
    )
    if error:
        return jsonify({'error': error}), status
    return jsonify(result), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task_route(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    result, error, status = update_task(task_id, data)
    if error:
        return jsonify({'error': error}), status
    return jsonify(result), status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_route(task_id):
    _, error, status = delete_task(task_id)
    if error:
        return jsonify({'error': error}), status
    return jsonify({'message': 'Task deletada com sucesso'}), status
