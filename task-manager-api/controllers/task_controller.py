import logging
from datetime import datetime
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from config.settings import DEFAULT_PRIORITY

logger = logging.getLogger(__name__)


def list_tasks():
    from sqlalchemy.orm import joinedload
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return [t.to_dict() for t in tasks]


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return None, "Task não encontrada", 404
    return task.to_dict(), None, 200


def create_task(title, description, status, priority, user_id, category_id, due_date, tags):
    if not title:
        return None, "Título é obrigatório", 400

    task = Task()
    task.title = title.strip()

    if not task.validate_status.__func__(task, status):
        return None, "Status inválido", 400
    if not task.validate_priority.__func__(task, priority):
        return None, "Prioridade deve ser entre 1 e 5", 400

    if user_id and not User.query.get(user_id):
        return None, "Usuário não encontrado", 404
    if category_id and not Category.query.get(category_id):
        return None, "Categoria não encontrada", 404

    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return None, "Formato de data inválido. Use YYYY-MM-DD", 400

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info("Task created id=%s title=%s", task.id, task.title)
    return task.to_dict(), None, 201


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return None, "Task não encontrada", 404

    if 'title' in data:
        title = data['title'].strip()
        if len(title) < 3 or len(title) > 200:
            return None, "Título deve ter entre 3 e 200 caracteres", 400
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if not task.validate_status(data['status']):
            return None, "Status inválido", 400
        task.status = data['status']

    if 'priority' in data:
        if not task.validate_priority(data['priority']):
            return None, "Prioridade deve ser entre 1 e 5", 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            return None, "Usuário não encontrado", 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            return None, "Categoria não encontrada", 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return None, "Formato de data inválido", 400
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    db.session.commit()
    logger.info("Task updated id=%s", task_id)
    return task.to_dict(), None, 200


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return False, "Task não encontrada", 404
    db.session.delete(task)
    db.session.commit()
    logger.info("Task deleted id=%s", task_id)
    return True, None, 200


def search_tasks(query, status, priority, user_id):
    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in tasks.all()]


def task_stats():
    from datetime import timezone
    total = Task.query.count()
    overdue_count = sum(1 for t in Task.query.filter(
        Task.status.notin_(['done', 'cancelled']),
        Task.due_date.isnot(None)
    ).all() if t.is_overdue())

    return {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': Task.query.filter_by(status='done').count(),
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': overdue_count,
        'completion_rate': round((Task.query.filter_by(status='done').count() / total) * 100, 2) if total > 0 else 0,
    }
