# Architecture Audit Report — code-smells-project

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~784 lines of code

Summary
CRITICAL: 7 | HIGH: 4 | MEDIUM: 5 | LOW: 6

Findings

[CRITICAL] SQL Injection via String Concatenation — 18+ Injection Points
File: models.py:28,48-49,57-60,68,92,109-110,126-128,140,148-150,157-165,174,188,193,220,224,279-281,291-297
Description: Every query that accepts user input builds SQL via string concatenation or f-strings.
             Examples:
               - models.py:28  -> "SELECT * FROM produtos WHERE id = " + str(id)
               - models.py:109 -> "SELECT ... WHERE email = '" + email + "' AND senha = '" + senha + "'"
               - models.py:291 -> query += " AND nome LIKE '%" + termo + "%'"
             All 4 CRUD domains (products, users, orders, search) are affected.
Impact: Complete database compromise. Authentication bypass with email `' OR '1'='1' --`.
        Data exfiltration of all users, products, and orders. Database destruction.
Recommendation: Replace ALL string concatenation with parameterized queries.
                Use cursor.execute("... WHERE id = ?", (id,)) for every query.

[CRITICAL] Hardcoded Secret Key
File: app.py:7
Description: app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
             Literal secret key committed to source code.
Impact: Session tokens can be forged. Any attacker with read access to source can impersonate any user.
Recommendation: SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")

[CRITICAL] Secret Key Leaked in Health Check API Response
File: controllers.py:289
Description: The /health endpoint returns "secret_key": "minha-chave-super-secreta-123" in the JSON response.
             Any unauthenticated caller receives the application secret.
Impact: Cryptographic key exposure. Enables JWT/session forgery by any internet user.
Recommendation: Remove secret_key from health check response entirely.

[CRITICAL] Plaintext Password Storage
File: models.py:122-131, database.py:75-79
Description: Passwords are stored as plaintext strings in the database.
             - database.py:76-79: Seed data with passwords "admin123", "123456", "senha123"
             - models.py:127: INSERT directly stores the senha parameter without hashing
Impact: Full credential theft if database is breached. All accounts compromised instantly.
Recommendation: Use werkzeug.security.generate_password_hash() before storing.
                Update login to use check_password_hash().

[CRITICAL] Passwords Returned in API Responses
File: models.py:83-84, models.py:98-99
Description: get_todos_usuarios() (line 83) and get_usuario_por_id() (line 98-99) both include
             "senha": row["senha"] in the returned dict.
             GET /usuarios and GET /usuarios/<id> expose all user passwords to any caller.
Impact: All user credentials harvested via a single unauthenticated GET request.
Recommendation: Remove "senha" field from all serialization functions.

[CRITICAL] Arbitrary SQL Execution Endpoint
File: app.py:59-78
Description: POST /admin/query accepts any SQL string from the request body and executes it:
             dados.get("sql", ""); cursor.execute(query)
             No authentication, no input validation, no restrictions.
Impact: Any caller can run DROP TABLE, SELECT all data, INSERT backdoor users.
        Equivalent to unauthenticated remote database shell access.
Recommendation: Delete this endpoint entirely.

[CRITICAL] Unprotected Database Reset Endpoint
File: app.py:47-57
Description: POST /admin/reset-db deletes all data from all tables with no authentication.
             Anyone can call this endpoint to wipe the entire database.
Impact: Complete data loss with a single unauthenticated HTTP request.
Recommendation: Delete this endpoint or protect with strong authentication + authorization.

[HIGH] God Methods in models.py — Business Logic Mixed with Data Access
File: models.py:133-169, models.py:235-273
Description: criar_pedido() (lines 133-169) performs stock validation, total calculation, order creation,
             item insertion, and stock decrement — all mixed in one model function.
             relatorio_vendas() (lines 256-262) contains discount tier business logic inside a
             data access function.
Impact: Untestable in isolation. Business rules cannot change without touching data access code.
Recommendation: Extract business logic to a controller layer. Models should only do data access.

[HIGH] Business Logic in controllers.py — Validation and Notifications
File: controllers.py:28-54, controllers.py:208-210, controllers.py:248-250
Description: Product creation/update validation (min/max length, category allowlist) is inline in
             route handlers. Fake notification calls (print EMAIL/SMS/PUSH) are inside the
             criar_pedido and atualizar_status_pedido route handlers.
Impact: Duplicated validation logic across multiple route handlers. Cannot test business rules
        without HTTP layer. Notification logic is not centralized.
Recommendation: Extract validation and notification logic to controller classes.

[HIGH] No Authentication or Authorization on Any Endpoint
File: app.py (all routes)
Description: Every endpoint — including /admin/reset-db, /admin/query, /usuarios (returns passwords),
             and /pedidos — is publicly accessible without any authentication.
Impact: Complete OWASP A01 (Broken Access Control) violation. Any internet user can access
        admin functions, view all user data, and place orders as any user.
Recommendation: Implement authentication middleware. At minimum, require a token for admin endpoints.

[HIGH] Debug Mode and 0.0.0.0 Binding in Production Code
File: app.py:7-8,88
Description: app.config["DEBUG"] = True is hardcoded. app.run(host="0.0.0.0", ..., debug=True)
             exposes the Werkzeug interactive debugger to the network.
Impact: Werkzeug debugger allows arbitrary Python code execution by any network-accessible client.
Recommendation: Extract DEBUG to env var. Use host="127.0.0.1" or let a WSGI server handle binding.

[MEDIUM] N+1 Query Problem in Order Retrieval
File: models.py:171-201, models.py:203-233
Description: get_pedidos_usuario() and get_todos_pedidos() both execute 3 nested query levels:
             1 query for orders, N queries for items per order, N*M queries for product names.
             The identical pattern is duplicated across both functions.
Impact: Performance degrades quadratically with data volume. 10 orders with 5 items each = 61 queries.
Recommendation: Replace with a single JOIN query. Group results in Python.

[MEDIUM] Code Duplication — Product Dict Construction
File: models.py:12-21, 31-40, 303-313
Description: The same 8-field product dict is assembled from row data in 3 separate functions.
             Any schema change requires updating 3 locations.
Impact: Inconsistent serialization if one location is missed during updates.
Recommendation: Extract to a helper function _row_to_product(row) called in all 3 places.

[MEDIUM] Code Duplication — Order+Items Loading Block
File: models.py:177-200, models.py:211-232
Description: The order-with-items loading block (~22 lines) is copy-pasted verbatim between
             get_pedidos_usuario() and get_todos_pedidos().
Impact: Bug fixes or schema changes must be applied to both functions.
Recommendation: Extract to a shared helper function _build_order_with_items(cursor, row).

[MEDIUM] SQL Injection in Search Function via Dynamic Query Building
File: models.py:285-299
Description: buscar_produtos() builds the WHERE clause by concatenating parameters:
             query += " AND nome LIKE '%" + termo + "%'"
             query += " AND categoria = '" + categoria + "'"
             Multiple concatenation points across different query branches.
Impact: Search endpoint is fully exploitable for data exfiltration or authentication bypass.
Recommendation: Use parameterized query with conditionally-built params list.

[MEDIUM] Global Mutable Database Connection
File: database.py:4,8-10
Description: db_connection = None is a module-level global mutated by get_db().
             check_same_thread=False disables SQLite's thread safety protection.
Impact: Under concurrent requests, shared mutable state can cause data corruption.
Recommendation: Use Flask application context (g object) for connection management.

[LOW] Magic Numbers in Discount Logic
File: models.py:257-262
Description: Discount thresholds (10000, 5000, 1000) and rates (0.1, 0.05, 0.02) are hardcoded
             with no named constants or documentation.
Impact: Changing business rules requires searching for magic numbers in code.
Recommendation: Extract to named constants: DISCOUNT_HIGH_THRESHOLD = 10000, etc.

[LOW] Print Statements Instead of Structured Logging
File: controllers.py:8,11,57,61,106,161,179,182,208-210,219,248,250 | app.py:56,83-86
Description: All logging uses print() with no severity levels, timestamps, or structured format.
Impact: No log levels (INFO/WARNING/ERROR). Cannot filter, search, or aggregate logs.
Recommendation: Replace with Python logging module: import logging; logger = logging.getLogger(__name__)

[LOW] Hardcoded Database Path
File: database.py:5
Description: db_path = "loja.db" is hardcoded. Not configurable without code changes.
Impact: Impossible to switch databases per environment (dev/test/prod) without modifying code.
Recommendation: DB_PATH = os.environ.get("DB_PATH", "loja.db")

[LOW] Hardcoded Port in Entry Point
File: app.py:88
Description: app.run(host="0.0.0.0", port=5000, debug=True) — port hardcoded.
Recommendation: PORT = int(os.environ.get("PORT", "5000"))

[LOW] Unused Import
File: models.py:2
Description: import sqlite3 is imported but never used directly (all access via get_db()).
Recommendation: Remove the unused import.

[LOW] CORS Wildcard — No Origin Restriction
File: app.py:9
Description: CORS(app) with no origin parameter allows cross-origin requests from any domain.
Impact: Any malicious website can make authenticated requests to this API.
Recommendation: CORS(app, origins=["https://yourdomain.com"]) or configure per environment.

================================
Total: 22 findings
================================
```
