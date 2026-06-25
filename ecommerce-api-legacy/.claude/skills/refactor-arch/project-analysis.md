# Project Analysis Reference

Heuristics for detecting language, framework, database, domain, and architecture of any backend project.

---

## Language Detection

### By Package Manifest (highest confidence)
| File | Language |
|------|----------|
| `requirements.txt`, `Pipfile`, `pyproject.toml`, `setup.py` | Python |
| `package.json` | Node.js / JavaScript |
| `package.json` with TypeScript in devDependencies | TypeScript |
| `Gemfile` | Ruby |
| `go.mod` | Go |
| `pom.xml`, `build.gradle` | Java |
| `composer.json` | PHP |

### By File Extensions (census method)
- Run: `Glob **/*.py` → Python if dominant
- Run: `Glob **/*.js` → Node.js if dominant
- Run: `Glob **/*.ts` → TypeScript if dominant
- The language with the most source files wins

### Exclusions when counting
Always exclude: `node_modules/`, `__pycache__/`, `.git/`, `venv/`, `env/`, `dist/`, `build/`, `*.min.js`, `*.pyc`

---

## Framework Detection

### Python Frameworks
Search `requirements.txt` or run `Grep "import flask|from flask"`:

| Signal | Framework |
|--------|-----------|
| `flask` in requirements or `from flask import` | Flask |
| `django` in requirements or `import django` | Django |
| `fastapi` in requirements or `from fastapi import` | FastAPI |
| `tornado` in requirements | Tornado |
| `bottle` in requirements | Bottle |
| `SQLAlchemy` in requirements | ORM: SQLAlchemy (framework-agnostic) |

### Node.js Frameworks
Search `package.json` dependencies:

| Signal | Framework |
|--------|-----------|
| `"express"` in dependencies | Express |
| `"fastify"` in dependencies | Fastify |
| `"koa"` in dependencies | Koa |
| `"@nestjs/core"` in dependencies | NestJS |
| `"hapi"` or `"@hapi/hapi"` | Hapi |

### Version Extraction
- Python: `flask==3.1.1` → version is `3.1.1`
- Node.js: `"express": "^4.18.2"` → version is `4.18.2`

---

## Database Technology Detection

### ORM Signals
| Signal | ORM / DB |
|--------|---------|
| `from flask_sqlalchemy import` or `from sqlalchemy import` | SQLAlchemy (Python) |
| `require('sequelize')` or `import { Sequelize }` | Sequelize (Node.js) |
| `require('mongoose')` or `import mongoose` | Mongoose / MongoDB |
| `require('@prisma/client')` | Prisma |
| `from django.db import models` | Django ORM |

### Raw Driver Signals
| Signal | DB Driver |
|--------|-----------|
| `import sqlite3` or `require('sqlite3')` or `require('better-sqlite3')` | SQLite |
| `import psycopg2` | PostgreSQL (Python) |
| `require('pg')` | PostgreSQL (Node.js) |
| `import pymysql` or `require('mysql2')` | MySQL |
| `require('mongodb')` | MongoDB raw driver |

### SQL Safety Assessment
**Parameterized (safe):**
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
db.query("SELECT * FROM users WHERE id = ?", [user_id])
```

**String concatenation (VULNERABLE):**
```python
cursor.execute("SELECT * FROM users WHERE id = " + str(id))
cursor.execute(f"SELECT * FROM users WHERE id = {id}")
cursor.execute("SELECT * FROM users WHERE id = " + id)
```

Run: `Grep "execute.*\+|execute.*f\"|execute.*format"` to find injection points.

---

## Domain Detection

### Route Path Analysis
Extract all route definitions and group by resource noun:

| Route Pattern | Domain Hint |
|--------------|-------------|
| `/products`, `/orders`, `/cart`, `/checkout` | E-commerce |
| `/courses`, `/enrollments`, `/lessons` | LMS / Education |
| `/tasks`, `/projects`, `/boards`, `/assignees` | Task Management |
| `/posts`, `/comments`, `/users`, `/follows` | Social / Blog |
| `/articles`, `/categories`, `/tags` | CMS |

### Model/Table Name Analysis
- Python SQLAlchemy: `class Product(db.Model):`
- SQLite raw: `CREATE TABLE produtos`
- Node.js: `db.run("CREATE TABLE IF NOT EXISTS courses")`

### Domain Classification Template
Format: `{Domain} API ({entity1}, {entity2}, {entity3})`
Examples:
- `E-commerce API (produtos, pedidos, usuarios)`
- `LMS API (courses, enrollments, users, payments)`
- `Task Manager API (tasks, users, categories)`

---

## Architecture Assessment

### Architecture Levels

**Monolithic** (everything in 1-4 files):
- Most logic in a single file or 2-3 files
- Routes, business logic, and DB access all mixed
- No separation directories
- Signal: 80%+ of LOC in 1-2 files

**Partially Organized** (directories exist, responsibilities misplaced):
- `models/`, `routes/`, or `services/` directories exist
- But logic is in the wrong layer (e.g., DB queries in routes, business logic in models)
- Service/utility files exist but are never called
- Signal: correct directory names but wrong code inside

**Layered** (clean separation):
- Distinct files per concern (models, controllers, routes)
- Each layer only does its job
- Clear entry point with dependency wiring

### Detection Signals
```
# Monolithic signals
- Single file > 200 lines with mixed imports (HTTP + DB)
- Route handlers > 30 lines
- SQL queries inside route/controller functions

# Partially organized signals
- models/ exists but has business logic
- services/ exists with classes that are never imported elsewhere
- Validation logic duplicated across multiple route files instead of being centralized
- Grep for service class name → only found in its own file (dead code)

# Count files per directory
Glob models/** → check if populated
Glob controllers/** → check if populated or missing
Glob routes/** → check if populated
```

---

## Output Template

After completing analysis, print exactly this block:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      {language}
Framework:     {framework_name} {version}
Dependencies:  {dep1}, {dep2}, {dep3}
Domain:        {domain_description}
Architecture:  {arch_level} — {brief_description}
Source files:  {N} files analyzed
DB technology: {db_tech} ({raw_sql_or_orm})
DB tables:     {table1}, {table2}, {table3}
================================
```

Example outputs:
```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuarios)
Architecture:  Monolithic — all logic in 4 files, no layer separation
Source files:  4 files analyzed
DB technology: SQLite (raw SQL with string concatenation)
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18.2
Dependencies:  sqlite3
Domain:        LMS API (courses, enrollments, users, payments)
Architecture:  Monolithic — God class AppManager contains all logic
Source files:  3 files analyzed
DB technology: SQLite (raw SQL, parameterized queries)
DB tables:     courses, users, enrollments, payments, audit_log
================================
```
