# MVC Architecture Guidelines

Target architecture for refactored projects. Applies to both Python/Flask and Node.js/Express.

---

## Core Principle: Layer Separation

Each layer has exactly one job. A layer must NEVER do another layer's job.

| Layer | Job | Must NOT |
|-------|-----|---------|
| Config | Provide configuration values | Contain business logic |
| Model | Data access only | Contain HTTP objects, validation of request payloads |
| Controller | Business logic, orchestration | Import Flask/Express, touch request/response |
| Route/View | HTTP handling | Contain business rules, SQL queries |
| Middleware | Cross-cutting concerns | Contain business logic |

---

## Python/Flask Target Structure

### For Monolithic Projects (e.g., code-smells-project)

```
{project-root}/
  src/
    config/
      __init__.py
      settings.py          # All config from env vars
    models/
      __init__.py
      product_model.py     # Product data access (parameterized queries)
      user_model.py        # User data access + password hashing
      order_model.py       # Order data access (JOINs, no N+1)
    controllers/
      __init__.py
      product_controller.py    # Product business rules
      user_controller.py       # User creation, login logic
      order_controller.py      # Order creation, stock management
      report_controller.py     # Report aggregation
    views/
      __init__.py
      product_routes.py    # Flask Blueprint, thin HTTP handlers
      user_routes.py
      order_routes.py
      report_routes.py
    middlewares/
      __init__.py
      error_handler.py     # Centralized @app.errorhandler
  app.py                   # create_app() factory function
  requirements.txt
```

### For Partially Organized Projects (e.g., task-manager-api)

Keep existing structure, refactor in-place, add missing layers:

```
{project-root}/
  config/
    __init__.py
    settings.py            # NEW: extract hardcoded values
  models/                  # KEEP: fix password hashing, remove sensitive fields from to_dict()
    __init__.py
    user.py
    task.py
    category.py
  controllers/             # NEW: extract logic from routes
    __init__.py
    user_controller.py
    task_controller.py
    category_controller.py
    report_controller.py
  routes/                  # KEEP: slim down to thin HTTP handlers
    __init__.py
    user_routes.py
    task_routes.py
    category_routes.py     # NEW: move category CRUD out of report_routes
    report_routes.py       # KEEP: remove category CRUD, keep reports only
  middlewares/             # NEW
    __init__.py
    error_handler.py
  utils/
    helpers.py             # KEEP: remove dead functions, keep useful ones
  app.py                   # UPDATE: register middlewares, add config
  database.py              # KEEP
```

---

## Node.js/Express Target Structure

### For God Class Projects (e.g., ecommerce-api-legacy)

```
{project-root}/
  src/
    config/
      settings.js          # All config from process.env
    models/
      userModel.js         # User DB operations
      courseModel.js       # Course DB operations
      enrollmentModel.js   # Enrollment + payment DB operations
      auditModel.js        # Audit log writes
    controllers/
      checkoutController.js    # Checkout business logic (async/await)
      reportController.js      # Financial report logic
      userController.js        # User management
    routes/
      checkoutRoutes.js        # Express Router, thin handlers
      reportRoutes.js
      userRoutes.js
    middlewares/
      errorHandler.js          # Express error middleware
    app.js                     # Express wiring (composition root)
  package.json
```

---

## Layer Responsibilities (Detailed)

### Config Layer

**What goes here**: Every value that might differ between environments.
- Secret keys, API keys, passwords
- Database connection strings, file paths
- Port numbers, host names
- Debug flags
- Feature flags

**Pattern**:
```python
# settings.py (Python)
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
DB_PATH = os.environ.get("DB_PATH", "loja.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
PORT = int(os.environ.get("PORT", "5000"))
```

```javascript
// settings.js (Node.js)
module.exports = {
  secretKey: process.env.SECRET_KEY || "dev-only-change-in-production",
  dbPath: process.env.DB_PATH || "./loja.db",
  port: parseInt(process.env.PORT || "3000"),
  debug: process.env.DEBUG === "true",
};
```

---

### Model Layer

**What goes here**: Database interaction only.
- SQL queries with parameterized placeholders
- ORM model definitions and simple queries
- Connection management
- Data mapping (rows → domain objects/dicts)

**What does NOT go here**:
- Business rules (discount calculations, status transitions)
- HTTP request/response objects
- Validation of business constraints (that's controller territory)
- Notification logic

**Pattern**:
```python
# product_model.py (Python)
def get_product_by_id(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return dict(row)

def create_product(name, description, price, stock, category):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, description, price, stock, category) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, stock, category)
    )
    conn.commit()
    return cursor.lastrowid
```

---

### Controller Layer

**What goes here**: Business logic and orchestration.
- Input validation (business rules: price must be positive, name must be 2-200 chars)
- Multi-step operations (create order: validate stock → create order → deduct stock → return result)
- Calling multiple models and combining results
- Business rule enforcement

**What does NOT go here**:
- `request` or `response` objects from Flask/Express
- `jsonify()` calls
- SQL queries directly

**Pattern**:
```python
# product_controller.py (Python)
from src.models import product_model

class ProductController:
    def create_product(self, name, description, price, stock, category):
        # Validation (business rules)
        if not name or len(name) < 2:
            return {"success": False, "error": "Nome deve ter pelo menos 2 caracteres"}
        if price < 0:
            return {"success": False, "error": "Preco nao pode ser negativo"}
        valid_categories = ["eletronicos", "roupas", "alimentos", "livros", "outros"]
        if category not in valid_categories:
            return {"success": False, "error": f"Categoria invalida. Use: {valid_categories}"}
        
        # Orchestration
        product_id = product_model.create_product(name, description, price, stock, category)
        return {"success": True, "id": product_id}
```

---

### Route/View Layer

**What goes here**: HTTP-only concerns.
- Parse request body and query parameters
- Call the appropriate controller
- Serialize the controller result to JSON
- Set HTTP status codes
- Register routes as Flask Blueprints or Express Routers

**What does NOT go here**:
- Business validation (min/max lengths, category whitelists)
- SQL queries
- Multi-step business operations

**Pattern**:
```python
# product_routes.py (Python)
from flask import Blueprint, request, jsonify
from src.controllers.product_controller import ProductController

product_bp = Blueprint("products", __name__)
controller = ProductController()

@product_bp.route("/produtos", methods=["POST"])
def criar_produto():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisicao invalido"}), 400
    
    result = controller.create_product(
        name=data.get("nome"),
        description=data.get("descricao", ""),
        price=data.get("preco", 0),
        stock=data.get("estoque", 0),
        category=data.get("categoria", "")
    )
    
    if not result["success"]:
        return jsonify({"erro": result["error"]}), 400
    return jsonify({"id": result["id"], "mensagem": "Produto criado"}), 201
```

---

### Middleware Layer

**What goes here**: Cross-cutting concerns.
- Centralized error handling
- Request logging
- CORS configuration
- Authentication/authorization (if present)

**Pattern**:
```python
# error_handler.py (Python)
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso nao encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify({"erro": "Erro interno do servidor"}), 500
```

```javascript
// errorHandler.js (Node.js)
function errorHandler(err, req, res, next) {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message || "Internal server error",
  });
}
module.exports = { errorHandler };
```

---

### Entry Point

**What goes here**: Application composition — wire everything together.
- Create the app instance
- Configure middleware
- Register blueprints/routers
- Start the server

**Pattern**:
```python
# app.py (Python - create_app factory)
from flask import Flask
from flask_cors import CORS
from src.config.settings import SECRET_KEY, DEBUG, PORT
from src.views.product_routes import product_bp
from src.views.user_routes import user_bp
from src.views.order_routes import order_bp
from src.middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG
    CORS(app)
    
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)
    
    register_error_handlers(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=PORT, debug=DEBUG)
```

---

## Adaptation Rules for Partially Organized Projects

1. **Don't rebuild what's good**: If `models/` already has ORM models, keep and improve them (fix password hashing, remove sensitive fields from `to_dict()`).

2. **Don't move what's correct**: If routes are already in separate Blueprint files, refactor in-place rather than creating a new `views/` directory.

3. **Add missing layers**: If `controllers/` doesn't exist, create it. Extract business logic from routes into controllers. Make routes thin.

4. **Wire up dead code**: If a service or utility function is defined but never called, and it's useful, wire it up. If it's duplicating logic that's already inline everywhere, delete the inline copies and call the canonical version.

5. **Fix, don't remove models**: If model validation methods (`validate_status()`, `is_overdue()`) exist but are never called, wire them up in the controller instead of re-implementing the same logic.

6. **Misplaced CRUD**: If Category CRUD is inside `report_routes.py`, extract it to `category_routes.py` rather than rewriting the handlers.
