import re
import logging
from database import db
from models.user import User
from models.task import Task
from config.settings import VALID_ROLES, MIN_PASSWORD_LENGTH

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def list_users():
    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = len(u.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado", 404
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data, None, 200


def create_user(name, email, password, role='user'):
    if not name:
        return None, "Nome é obrigatório", 400
    if not email:
        return None, "Email é obrigatório", 400
    if not password:
        return None, "Senha é obrigatória", 400
    if not EMAIL_REGEX.match(email):
        return None, "Email inválido", 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return None, f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres", 400
    if role not in VALID_ROLES:
        return None, "Role inválido", 400

    if User.query.filter_by(email=email).first():
        return None, "Email já cadastrado", 409

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()
    logger.info("User created id=%s email=%s", user.id, email)
    return user.to_dict(), None, 201


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado", 404

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not EMAIL_REGEX.match(data['email']):
            return None, "Email inválido", 400
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return None, "Email já cadastrado", 409
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return None, f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres", 400
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            return None, "Role inválido", 400
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict(), None, 200


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return False, "Usuário não encontrado", 404

    for task in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()
    logger.info("User deleted id=%s", user_id)
    return True, None, 200


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado", 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    return [t.to_dict() for t in tasks], None, 200


def login(email, password):
    if not email or not password:
        return None, "Email e senha são obrigatórios", 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, "Credenciais inválidas", 401

    if not user.active:
        return None, "Usuário inativo", 403

    logger.info("Login successful email=%s", email)
    return user.to_dict(), None, 200
