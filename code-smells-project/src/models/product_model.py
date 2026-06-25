from database import get_db


def _row_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE ativo = 1")
    return [_row_to_dict(row) for row in cursor.fetchall()]


def get_by_id(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def create(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def update(product_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, product_id),
    )
    db.commit()
    return True


def delete(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    db.commit()
    return True


def search(termo=None, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM produtos WHERE ativo = 1"
    params = []

    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor.execute(query, params)
    return [_row_to_dict(row) for row in cursor.fetchall()]
