from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db


def _row_to_dict(row):
    # Password hash is intentionally excluded from all responses
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_row_to_dict(row) for row in cursor.fetchall()]


def get_by_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def create(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    hashed = generate_password_hash(senha)
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, hashed, tipo),
    )
    db.commit()
    return cursor.lastrowid


def authenticate(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row and check_password_hash(row["senha"], senha):
        return _row_to_dict(row)
    return None
