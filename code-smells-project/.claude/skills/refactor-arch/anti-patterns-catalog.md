# Anti-Patterns Catalog

Reference for the architectural audit. Each pattern has detection signals (grep-able), severity, and classification rationale.

---

## CRITICAL Severity

### AP-01: SQL Injection via String Concatenation

**Severity**: CRITICAL
**Description**: SQL queries built by concatenating user-controlled input directly into the query string. Allows attackers to manipulate the query, extract all data, bypass authentication, or destroy the database.

**Detection Signals** (use Grep):
```
# Python - string concatenation
"execute.*\" \+" 
"execute.*\+ str\("
"execute.*f\""
"execute.*\.format\("
"execute.*% "

# Specific patterns
"WHERE id = \" +"
"WHERE.*email.*=.*\" +"
"LIKE.*'%\" +"
```

**NOT a vulnerability** (parameterized - safe to ignore):
```python
cursor.execute("SELECT * FROM x WHERE id = ?", (id,))
cursor.execute("SELECT * FROM x WHERE id = %s", (id,))
db.run("SELECT * FROM x WHERE id = ?", [id])
```

**Impact**: Complete database compromise. Authentication bypass via `' OR '1'='1`. Data exfiltration. Data destruction.
**Recommendation**: Replace all string concatenation with parameterized queries using `?` placeholders and tuple arguments.

---

### AP-02: Hardcoded Credentials and Secrets

**Severity**: CRITICAL
**Description**: Passwords, API keys, secret keys, and other credentials stored as literal string values in source code. Once committed to version control, these secrets are permanently exposed.

**Detection Signals**:
```
# Secret key
"SECRET_KEY.*=.*\"[^{]"
"secret_key.*=.*'[^{]"

# Database credentials
"dbPass.*:.*\""
"db_password.*=.*\""
"password.*=.*\"[a-z0-9]"

# API keys (live keys always start with recognizable prefixes)
"pk_live_"
"sk_live_"
"paymentGatewayKey.*:"
"api_key.*=.*\""

# Email credentials
"email_password.*=.*\""
"smtp.*password.*=.*\""
```

**Impact**: Full system compromise if leaked. Cannot be rotated without code changes. Permanently exposed in git history.
**Recommendation**: Extract to environment variables. Use `os.environ.get("SECRET_KEY")` or `process.env.SECRET_KEY`. Add `.env` to `.gitignore`.

---

### AP-03: Sensitive Data Exposure in API Responses

**Severity**: CRITICAL
**Description**: Password hashes, secret keys, card numbers, or other sensitive fields returned in API responses or logged to console. This includes serialization functions that include password fields and logging statements that print credentials.

**Detection Signals**:
```
# Password in serialization (Python)
"\"senha\".*:.*self\.senha"
"\"password\".*:.*self\.password"
"row\[\"senha\"\]"
"row\[\"password\"\]"

# Secret key in response
"secret_key.*:.*app\.config"
"SECRET_KEY.*response"

# Credit card or sensitive data in logs
"console\.log.*cc"
"console\.log.*card"
"print.*senha"
"print.*password"

# API key in logs
"console\.log.*Key\|console\.log.*key\|console\.log.*token"
```

**Impact**: Credential theft from every API call. PCI-DSS violation if card data involved. User account compromise at scale.
**Recommendation**: Remove sensitive fields from serialization methods. Never log passwords, card numbers, or API keys.

---

### AP-04: Arbitrary Code/SQL Execution Endpoint

**Severity**: CRITICAL
**Description**: An HTTP endpoint that accepts raw SQL or code from the request body and executes it directly on the database or runtime. Equivalent to providing a remote shell.

**Detection Signals**:
```
# Python - raw SQL from request
"cursor\.execute\(query\)"
"cursor\.execute\(sql\)"
"cursor\.execute\(dados"
"\.get\(\"sql\"\)"
"eval\(request"
"exec\(request"

# Node.js
"db\.run\(req\.body"
"db\.all\(req\.body"
"eval\(req\.body"
```

**Impact**: Complete database access without authentication. Can drop tables, extract all data, or execute administrative commands.
**Recommendation**: Delete the endpoint entirely. If dynamic queries are needed, use an allowlist of known-safe queries.

---

## HIGH Severity

### AP-05: God Class / God Module

**Severity**: HIGH
**Description**: A single class or file that handles all application responsibilities: routing, business logic, database access, authentication, error handling. Violates Single Responsibility Principle.

**Detection Signals**:
```
# Python - single file with many responsibilities
# Check if one file imports both HTTP framework AND database
"from flask import.*\nfrom.*database import\|import sqlite3"

# Node.js - class with route setup AND business logic AND DB
"setupRoutes\|initDb\|checkout\|report"  # Multiple concerns in same class

# File size signal - any single file over 200 lines doing multiple things
# Use Glob + Read to check line counts
```

**Structural indicators**:
- Single file has `app.route()` decorators AND SQL queries AND business rules
- A class has methods for: routing setup, DB initialization, business operations, error handling
- `Grep` for import statements: if one file imports HTTP framework + DB driver + all business modules, it's doing too much

**Impact**: Untestable in isolation. Any change risks breaking everything. Cannot be worked on by multiple developers simultaneously.
**Recommendation**: Decompose by responsibility. Each layer (Model/Controller/Route) gets its own file. Apply the God Class Decomposition pattern from the playbook.

---

### AP-06: Insecure Password Handling

**Severity**: HIGH
**Description**: Passwords stored in plaintext, using MD5 (cryptographically broken, fast hash with no salt), or using a custom "encryption" function that is not a real password hashing algorithm.

**Detection Signals**:
```
# MD5 for passwords
"hashlib\.md5"
"md5.*encode\(\)"
"md5.*password\|password.*md5"

# Custom fake crypto
"badCrypto\|fakeCrypto\|customHash"
"btoa.*10000\|repeat.*10000"  # Repeated encoding is not hashing

# Node.js - no bcrypt/argon2
# Check if package.json has bcrypt, argon2, or scrypt
# If not, and passwords are stored, flag as HIGH

# Plaintext password storage
"password.*=.*request\.get_json\(\).*\n.*db.*INSERT"  # No hashing between read and store
```

**Impact**: If the database is breached, all passwords are immediately compromised. MD5 can be cracked in milliseconds using rainbow tables.
**Recommendation**: Use `werkzeug.security.generate_password_hash` (Python/Flask) or `bcrypt.hashSync(pwd, 10)` (Node.js). Never store plaintext or MD5.

---

## MEDIUM Severity

### AP-07: N+1 Query Problem

**Severity**: MEDIUM
**Description**: Executing N additional database queries inside a loop that already processes results from 1 query. Results in O(N) or O(N²) database calls when 1-2 queries with JOINs would suffice.

**Detection Signals**:
```
# Python - query inside a for loop
"for.*in.*:\n.*cursor\.execute"
"for.*in.*:\n.*\.query\."
"for.*in.*:\n.*db\."

# SQLAlchemy lazy loading in loop
"for.*in.*:\n.*\.query\.get\("
"for.*in.*:\n.*User\.query"
"for.*in.*:\n.*Category\.query"

# Node.js - db call in callback/loop
"forEach.*function.*db\."
"for.*of.*db\.get\|db\.all"
```

**Impact**: Response times grow linearly with data. 100 records = 101+ queries. Will cause timeouts at scale.
**Recommendation**: Replace with JOIN queries or batch SELECT with IN clause. For ORMs, use eager loading (`joinedload` in SQLAlchemy).

---

### AP-08: Business Logic in Route/Handler Layer

**Severity**: MEDIUM
**Description**: Route handlers (Flask view functions, Express route handlers) contain complex business logic: validation rules, calculations, discount tiers, status transitions, notification triggers. This logic belongs in a Controller or Service layer.

**Detection Signals**:
```
# Python route functions with too many lines
# Read route files and check handler length > 30 lines

# Business signals inside route handlers
"@app\.route.*\ndef.*:.*\n.*if.*len\("    # Validation in route
"@app\.route.*\ndef.*:.*\n.*\* 0\."       # Calculation in route
"@app\.route.*\ndef.*:.*\n.*print.*notif" # Notification in route

# Node.js
"router\.(get|post|put|delete).*async.*req.*res.*{[\s\S]{500,}}"  # Handler > 500 chars
```

**Structural check**: Read each route file. If any handler function contains:
- Price calculations
- Discount tier logic
- Status validation (checking valid values)
- Stock management
- Multi-step database operations
→ Flag as business logic in wrong layer.

**Impact**: Duplicated validation logic across multiple routes. Cannot test business rules without HTTP layer. Changes to business rules require modifying multiple route files.
**Recommendation**: Extract to a Controller module. Route only parses request, calls controller, serializes response.

---

### AP-09: Dead Code and Unused Modules

**Severity**: MEDIUM
**Description**: Service classes, utility functions, or validation methods that are defined but never called. Often appears in partially-organized projects where structure was created but never wired up.

**Detection Signals**:
```
# Find defined functions and check if they're called elsewhere
# For each function/class in services/ or utils/:
# 1. Get the function/class name
# 2. Grep for it across the entire codebase
# 3. If it only appears in its own file → dead code

# Python - model methods never called
# Example: Task.validate_status() defined but never imported/called
"def validate_status\|def validate_priority\|def is_overdue"  # Defined
# Then check: Grep "validate_status\|validate_priority\|is_overdue" in routes/ and controllers/

# Python - unused imports
"^import os, sys, json\|^import json, os"  # Multiple imports, check which are used
"^from.*import.*\n(?!.*use)"  # Import not followed by usage

# Node.js - exported but never required
"module\.exports.*=.*{[\s\S]*}"  # Find exports
# Then Grep for each exported name in other files
```

**Impact**: Code bloat. Developers maintain code that does nothing. Logic is duplicated inline instead of being centralized.
**Recommendation**: Either wire up the dead code properly (if it's useful) or delete it. Call existing validation methods instead of duplicating logic inline.

---

### AP-10: Deprecated API Usage

**Severity**: MEDIUM
**Description**: Use of APIs that have been deprecated in the current or recent versions of the language/framework/library. Deprecated APIs may be removed in future versions, causing runtime failures.

**Detection Signals**:
```
# Python - datetime.utcnow() deprecated since Python 3.12
"datetime\.utcnow\(\)"

# Python - bare except (considered bad practice, hides bugs)
"^    except:$\|^        except:$"

# Node.js - new Buffer() deprecated since Node.js 6
"new Buffer\("

# Python - MD5 for security purposes (cryptographically deprecated)
"hashlib\.md5"

# Flask - before_request returning value (behavior changed)
# Express - app.use(express.bodyParser()) (removed in Express 4)
"express\.bodyParser\(\)"
"res\.send\([0-9]{3},"  # Old Express res.send(statusCode, body) signature

# SQLite3 Node.js - callback-based API (prefer better-sqlite3 sync API or promisify)
"db\.run\(.*function.*err"  # Old callback pattern vs async/await
```

**Impact**: Silent failures in newer versions. Security vulnerabilities from deprecated crypto. Maintenance burden.
**Recommendation**:
- `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `new Buffer()` → `Buffer.from()`
- MD5 for passwords → `werkzeug.security` or `bcrypt`
- Bare `except:` → `except Exception as e:`
