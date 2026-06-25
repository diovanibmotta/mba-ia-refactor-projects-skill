import logging
from database import db
from models.category import Category
from models.task import Task

logger = logging.getLogger(__name__)


def list_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        data = c.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return result


def create_category(name, description='', color='#000000'):
    if not name:
        return None, "Nome é obrigatório", 400
    category = Category()
    category.name = name
    category.description = description
    category.color = color
    db.session.add(category)
    db.session.commit()
    logger.info("Category created id=%s name=%s", category.id, name)
    return category.to_dict(), None, 201


def update_category(cat_id, data):
    cat = Category.query.get(cat_id)
    if not cat:
        return None, "Categoria não encontrada", 404
    if not data:
        return None, "Dados inválidos", 400
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']
    db.session.commit()
    return cat.to_dict(), None, 200


def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return False, "Categoria não encontrada", 404
    db.session.delete(cat)
    db.session.commit()
    logger.info("Category deleted id=%s", cat_id)
    return True, None, 200
