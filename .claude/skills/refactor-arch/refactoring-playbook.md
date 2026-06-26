# Refactoring Playbook

Concrete transformation patterns with before/after code examples for both Python and Node.js.

---

## Pattern 1: Extract Configuration

**Applies when**: AP-02 (Hardcoded Credentials/Secrets)

**Before (Python)**:
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True

# database.py
db_path = "loja.db"
```

**After (Python)**:
```python
# config/settings.py
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-default")
DB_PATH = os.environ.get("DB_PATH", "loja.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
PORT = int(os.environ.get("PORT", "5000"))

# app.py
from src.config.settings import SECRET_KEY, DEBUG, PORT
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG
```

**Before (Node.js)**:
```javascript
// utils.js
const config = {
  dbUser: "admin_master",
  dbPass: "senha_super_secreta_prod_123",
  paymentGatewayKey: "pk_live_1234567890abcdef",
};
```

**After (Node.js)**:
```javascript
// config/settings.js
module.exports = {
  dbPath: process.env.DB_PATH || "./loja.db",
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  secretKey: process.env.SECRET_KEY || "dev-only-insecure-default",
  port: parseInt(process.env.PORT || "3000"),
};
```

**Steps**:
1. Create `config/settings.py` or `config/settings.js`
2. Scan all files for string literals assigned to credential-sounding variable names
3. Move each to config module as `os.environ.get()` or `process.env.VAR`
4. Update all import sites to use config module
5. Create `.env.example` with dummy values showing which vars to set

---

## Pattern 2: SQL Injection → Parameterized Queries

**Applies when**: AP-01 (SQL Injection via String Concatenation)

**Before (Python)**:
```python
# String concatenation — VULNERABLE
cursor.execute("SELECT * FROM users WHERE id = " + str(id))
cursor.execute("SELECT * FROM users WHERE email = '" + email + "' AND senha = '" + senha + "'")
cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{term}%'")
cursor.execute("INSERT INTO products (name, price) VALUES ('" + name + "', " + str(price) + ")")
```

**After (Python)**:
```python
# Parameterized queries — SAFE
cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
cursor.execute("SELECT * FROM users WHERE email = ? AND senha = ?", (email, senha))
cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{term}%",))
cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
```

**Steps**:
1. Find all `cursor.execute()` calls with string concatenation (see AP-01 detection signals)
2. Replace each with `?` placeholder and tuple argument
3. Note: `?` is for sqlite3; use `%s` for psycopg2 (PostgreSQL)
4. For LIKE queries, build the `%term%` string in Python BEFORE passing to execute

---

## Pattern 3: Extract Business Logic to Controllers

**Applies when**: AP-08 (Business Logic in Route/Handler Layer)

**Before (Python)**:
```python
# controllers.py (Flask route handler doing everything)
@app.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400
    
    nome = dados.get("nome", "")
    preco = dados.get("preco", 0)
    categoria = dados.get("categoria", "")
    
    # Business validation — should not be here
    if not nome or len(nome) < 2 or len(nome) > 200:
        return jsonify({"erro": "Nome invalido"}), 400
    if preco < 0:
        return jsonify({"erro": "Preco negativo"}), 400
    categorias_validas = ["eletronicos", "roupas", "alimentos", "livros", "outros"]
    if categoria not in categorias_validas:
        return jsonify({"erro": "Categoria invalida"}), 400
    
    # Direct model call with business logic mixed in
    id = models.criar_produto(nome, dados.get("descricao",""), preco, dados.get("estoque",0), categoria)
    return jsonify({"id": id, "mensagem": "Produto criado"}), 201
```

**After (Python)**:
```python
# controllers/product_controller.py
from src.models import product_model

VALID_CATEGORIES = ["eletronicos", "roupas", "alimentos", "livros", "outros"]

class ProductController:
    def create_product(self, name, description, price, stock, category):
        if not name or len(name) < 2 or len(name) > 200:
            return {"success": False, "error": "Nome deve ter 2-200 caracteres"}
        if price < 0:
            return {"success": False, "error": "Preco nao pode ser negativo"}
        if category not in VALID_CATEGORIES:
            return {"success": False, "error": f"Categoria invalida. Use: {VALID_CATEGORIES}"}
        product_id = product_model.create_product(name, description, price, stock, category)
        return {"success": True, "id": product_id}

# views/product_routes.py
from flask import Blueprint, request, jsonify
from src.controllers.product_controller import ProductController

product_bp = Blueprint("products", __name__)
controller = ProductController()

@product_bp.route("/produtos", methods=["POST"])
def criar_produto():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo invalido"}), 400
    result = controller.create_product(
        name=data.get("nome", ""),
        description=data.get("descricao", ""),
        price=data.get("preco", 0),
        stock=data.get("estoque", 0),
        category=data.get("categoria", "")
    )
    if not result["success"]:
        return jsonify({"erro": result["error"]}), 400
    return jsonify({"id": result["id"], "mensagem": "Produto criado"}), 201
```

**Steps**:
1. Create `controllers/` directory with `__init__.py`
2. For each domain (product, user, order, etc.), create `{domain}_controller.py`
3. Move validation logic and business rules from route handlers to controller methods
4. Controller methods receive plain Python objects (strings, ints, dicts) — no request objects
5. Controller returns result dict with `{"success": True/False, "data": ..., "error": ...}`
6. Route handler becomes thin: parse request → call controller → return jsonify

---

## Pattern 4: God Class Decomposition

**Applies when**: AP-05 (God Class / God Module)

**Before (Node.js)**:
```javascript
// AppManager.js — does EVERYTHING
class AppManager {
  constructor(db) { this.db = db; }
  
  initDb() { /* schema creation */ }
  setupRoutes(app) {
    app.post("/api/checkout", (req, res) => {
      // 50 lines of checkout logic with N+1 queries and callback hell
    });
    app.get("/api/admin/financial-report", (req, res) => {
      // 49 lines of report with nested N+1 queries
    });
  }
}
```

**After (Node.js)**:
```javascript
// models/courseModel.js
const getCourseById = (db, courseId) => {
  return new Promise((resolve, reject) => {
    db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [courseId], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
};
module.exports = { getCourseById };

// controllers/checkoutController.js
const { getCourseById } = require("../models/courseModel");
const { createOrFindUser } = require("../models/userModel");

const checkout = async (db, name, email, password, courseId, cardNumber) => {
  const course = await getCourseById(db, courseId);
  if (!course) return { success: false, status: 404, error: "Course not found" };
  
  const user = await createOrFindUser(db, name, email, password);
  const paymentStatus = cardNumber.startsWith("4") ? "PAID" : "DENIED";
  
  // ... rest of logic
  return { success: true, data: { enrollment, payment } };
};

module.exports = { checkout };

// routes/checkoutRoutes.js
const express = require("express");
const { checkout } = require("../controllers/checkoutController");

const router = express.Router();

router.post("/api/checkout", async (req, res, next) => {
  try {
    const { name, email, password, courseId, cardNumber } = req.body;
    if (!name || !email || !courseId || !cardNumber) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const result = await checkout(req.app.locals.db, name, email, password, courseId, cardNumber);
    if (!result.success) return res.status(result.status).json({ error: result.error });
    res.status(200).json(result.data);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
```

**Steps**:
1. List all methods/functions by responsibility type (DB, business, HTTP)
2. Group: DB operations → models, business logic → controllers, HTTP handling → routes
3. Create files for each group
4. Migrate methods, updating imports as needed
5. Wire together in `app.js`

---

## Pattern 5: Secure Password Handling

**Applies when**: AP-06 (Insecure Password Handling)

**Before (Python — MD5)**:
```python
import hashlib
self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

**After (Python — werkzeug)**:
```python
from werkzeug.security import generate_password_hash, check_password_hash

# In model set_password method:
self.password_hash = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password_hash, pwd)
```

**Before (Node.js — fake crypto)**:
```javascript
function badCrypto(str) {
  let result = str;
  for (let i = 0; i < 10000; i++) result = btoa(result).substring(0, 2) + result;
  return result.substring(0, 10);
}
```

**After (Node.js — bcrypt)**:
```javascript
const bcrypt = require("bcrypt");

async function hashPassword(plaintext) {
  return bcrypt.hash(plaintext, 10);
}

async function verifyPassword(plaintext, hash) {
  return bcrypt.compare(plaintext, hash);
}
```

**Steps**:
1. Add `werkzeug` to requirements.txt (Python) or `bcrypt` to package.json (Node.js)
2. Update model to use secure hashing
3. Update column name if needed (e.g., `password` → `password_hash`)
4. Update any login logic to use the new verify function
5. Note: Existing stored passwords (in seeds or DB) will need to be re-hashed

---

## Pattern 6: Remove Sensitive Data from API Responses

**Applies when**: AP-03 (Sensitive Data Exposure)

**Before (Python)**:
```python
def to_dict(self):
    return {
        "id": self.id,
        "email": self.email,
        "password": self.password,   # NEVER expose this
        "role": self.role,
    }
```

**After (Python)**:
```python
def to_dict(self):
    return {
        "id": self.id,
        "email": self.email,
        # password field removed entirely
        "role": self.role,
    }
```

**Before (Python — raw dict)**:
```python
# models.py
return {
    "id": row["id"],
    "email": row["email"],
    "senha": row["senha"],   # NEVER return this
}
```

**After (Python)**:
```python
return {
    "id": row["id"],
    "email": row["email"],
    # senha field removed
}
```

**Before (Node.js — logging sensitive data)**:
```javascript
console.log(`Processando cartao ${cc} na chave ${config.paymentGatewayKey}`);
```

**After (Node.js)**:
```javascript
console.log("Processing payment for enrollment");  // No sensitive data
```

**Steps**:
1. Find all `to_dict()` methods and serialization functions
2. Remove password, hash, and credential fields
3. Find all `console.log` / `print` statements near credential variables
4. Replace with generic log messages that don't include sensitive values

---

## Pattern 7: Fix N+1 Queries

**Applies when**: AP-07 (N+1 Query Problem)

**Before (Python — nested queries in loop)**:
```python
# N+1+1: 1 query for orders, N for items, N*M for products
def get_pedidos_usuario(usuario_id):
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    pedidos = cursor.fetchall()
    result = []
    for pedido in pedidos:
        cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
        itens = cursor.fetchall()
        itens_list = []
        for item in itens:
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],))
            produto = cursor.fetchone()
            itens_list.append({...item, "produto": produto})
        result.append({...pedido, "itens": itens_list})
    return result
```

**After (Python — JOIN)**:
```python
def get_pedidos_usuario(usuario_id):
    cursor.execute("""
        SELECT p.*, ip.quantidade, ip.preco_unitario,
               pr.nome as produto_nome, pr.categoria
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.id
    """, (usuario_id,))
    rows = cursor.fetchall()
    # Group by order ID in Python
    orders = {}
    for row in rows:
        order_id = row["id"]
        if order_id not in orders:
            orders[order_id] = {"id": order_id, "total": row["total"], "itens": []}
        if row["quantidade"]:
            orders[order_id]["itens"].append({
                "quantidade": row["quantidade"],
                "produto": row["produto_nome"]
            })
    return list(orders.values())
```

**Before (SQLAlchemy — lazy load in loop)**:
```python
tasks = Task.query.all()
for task in tasks:
    user = User.query.get(task.user_id)   # N extra queries
    category = Category.query.get(task.category_id)  # N extra queries
```

**After (SQLAlchemy — eager loading)**:
```python
from sqlalchemy.orm import joinedload
tasks = Task.query.options(
    joinedload(Task.user),
    joinedload(Task.category)
).all()
# No extra queries — user and category loaded in 1-2 queries total
```

**Steps**:
1. Identify any `cursor.execute()` or `.query.get()` inside a `for` loop
2. For raw SQL: rewrite as a JOIN query, group results in Python
3. For SQLAlchemy ORM: add `joinedload()` to the initial query
4. Verify the result shape is the same as before

---

## Pattern 8: Centralized Error Handling

**Applies when**: Scattered try/except in every route

**Before (Python)**:
```python
# Every route has its own error handling
@app.route("/produtos")
def get_produtos():
    try:
        produtos = models.get_todos_produtos()
        return jsonify(produtos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500  # Leaks internal details!

@app.route("/usuarios")
def get_usuarios():
    try:
        usuarios = models.get_todos_usuarios()
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
```

**After (Python)**:
```python
# middlewares/error_handler.py
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso nao encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled error: {type(e).__name__}: {str(e)}", exc_info=True)
        return jsonify({"erro": "Erro interno do servidor"}), 500

# app.py
from src.middlewares.error_handler import register_error_handlers
register_error_handlers(app)

# routes (simplified — no try/except needed for unhandled errors)
@product_bp.route("/produtos")
def get_produtos():
    produtos = product_model.get_all_products()
    return jsonify(produtos)
```

**Before (Node.js)**:
```javascript
// Every handler has its own error handling
router.get("/report", (req, res) => {
  try {
    // ...logic
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
```

**After (Node.js)**:
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === "production" ? "Internal server error" : err.message,
  });
}
module.exports = { errorHandler };

// app.js — register LAST
const { errorHandler } = require("./middlewares/errorHandler");
app.use(errorHandler);

// routes (use next(err) instead of try/catch everywhere)
router.get("/report", async (req, res, next) => {
  try {
    const data = await reportController.getReport(db);
    res.json(data);
  } catch (err) {
    next(err);  // Delegate to centralized handler
  }
});
```

---

## Pattern 9: Callback Hell → Async/Await (Node.js)

**Applies when**: AP-10 (Deprecated API / Callback Hell in Node.js)

**Before (Node.js — deeply nested callbacks)**:
```javascript
app.post("/api/checkout", (req, res) => {
  db.get("SELECT * FROM courses WHERE id = ?", [req.body.cid], (err, course) => {
    if (err) return res.status(500).send(err.message);
    if (!course) return res.status(404).send("Course not found");
    db.get("SELECT * FROM users WHERE email = ?", [req.body.e], (err, user) => {
      if (err) return res.status(500).send(err.message);
      if (!user) {
        db.run("INSERT INTO users ...", [...], function(err) {
          if (err) return res.status(500).send(err.message);
          // ...more nesting
        });
      }
    });
  });
});
```

**After (Node.js — async/await with promisified sqlite3)**:
```javascript
// models/db.js — promisify sqlite3
const { promisify } = require("util");

function getDb(db) {
  return {
    get: promisify(db.get.bind(db)),
    all: promisify(db.all.bind(db)),
    run: (sql, params) => new Promise((resolve, reject) => {
      db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    }),
  };
}

// controllers/checkoutController.js
const checkout = async (db, { name, email, password, courseId, cardNumber }) => {
  const pdb = getDb(db);
  
  const course = await pdb.get("SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
  if (!course) throw Object.assign(new Error("Course not found"), { status: 404 });
  
  let user = await pdb.get("SELECT * FROM users WHERE email = ?", [email]);
  if (!user) {
    const hash = await bcrypt.hash(password || "changeme", 10);
    const result = await pdb.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [name, email, hash]);
    user = { id: result.lastID, name, email };
  }
  
  // ... flat, readable logic
  return { success: true, user, course };
};
```

---

## Pattern 10: Wire Up / Remove Dead Code

**Applies when**: AP-09 (Dead Code and Unused Modules)

**Before (Python — model methods exist but never called)**:
```python
# models/task.py — validate_status() defined but never used
def validate_status(self, new_status):
    valid = ["pending", "in_progress", "done", "cancelled"]
    return new_status in valid

# routes/task_routes.py — validation duplicated inline instead
valid_statuses = ["pending", "in_progress", "done", "cancelled"]
if data.get("status") and data["status"] not in valid_statuses:
    return jsonify({"error": "Invalid status"}), 400
```

**After (Python — wire up existing method)**:
```python
# controllers/task_controller.py
from models.task import Task

class TaskController:
    def update_task(self, task_id, data):
        task = Task.query.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found", "status": 404}
        
        if "status" in data:
            if not task.validate_status(data["status"]):  # Use the model method!
                return {"success": False, "error": "Invalid status", "status": 400}
            task.status = data["status"]
        # ...
        return {"success": True, "task": task.to_dict()}

# routes/task_routes.py — no more inline validation
@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json() or {}
    result = controller.update_task(task_id, data)
    if not result["success"]:
        return jsonify({"error": result["error"]}), result.get("status", 400)
    return jsonify(result["task"])
```

**Before (Python — dead service never imported)**:
```python
# services/notification_service.py exists but no file imports it
class NotificationService:
    def send_email(self, to, subject, body): ...
```

**After — two options**:

Option A (Wire up if useful):
```python
# controllers/task_controller.py
from services.notification_service import NotificationService

notification_service = NotificationService()

def create_task(self, data):
    task = # ... create task
    notification_service.send_email(
        to=task.user.email,
        subject="New task assigned",
        body=f"Task '{task.title}' has been assigned to you."
    )
    return {"success": True, "task": task.to_dict()}
```

Option B (Delete if not needed):
```python
# Delete services/notification_service.py entirely
# Remove any imports of it
```

**Steps**:
1. For each function/class in `services/` and `utils/`: grep its name across the whole project
2. If it appears ONLY in its own file → dead code
3. Decide: wire up (if the functionality is needed) or delete (if truly unused)
4. If wiring up: add import in controller, call the method instead of inline duplicate
5. Remove inline duplicates in routes
