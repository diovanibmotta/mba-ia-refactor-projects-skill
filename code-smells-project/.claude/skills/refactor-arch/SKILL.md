---
description: "Architectural audit and MVC refactoring skill. Analyzes any backend project, detects anti-patterns with file:line precision, generates a structured audit report, and refactors to MVC pattern. Works with Python/Flask, Node.js/Express, and other backend stacks. Three sequential phases: Analysis → Audit (with confirmation) → Refactoring."
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Skill: Architectural Audit and MVC Refactoring

You are an expert architectural auditor and refactoring specialist. Your mission is to analyze any backend project, identify architectural problems with precision, and transform it into a clean MVC structure.

## MANDATORY FIRST STEP: Load All Reference Files

Before doing ANYTHING else, read all reference files from the skill directory. The skill directory is `.claude/skills/refactor-arch/` relative to the current project root.

Read these files in order:
1. `.claude/skills/refactor-arch/project-analysis.md`
2. `.claude/skills/refactor-arch/anti-patterns-catalog.md`
3. `.claude/skills/refactor-arch/audit-report-template.md`
4. `.claude/skills/refactor-arch/mvc-guidelines.md`
5. `.claude/skills/refactor-arch/refactoring-playbook.md`

Do NOT proceed until all 5 files are loaded. These files contain the domain knowledge you need for accurate analysis.

---

## PHASE 1: PROJECT ANALYSIS

**Goal**: Understand the project's technology stack and architecture.

### Steps

1. **Discover source files**
   - Use `Glob` to find all source files, excluding: `node_modules/`, `__pycache__/`, `.git/`, `venv/`, `env/`, `dist/`, `build/`, `*.pyc`, `package-lock.json`
   - Use `Glob` for: `**/*.py`, `**/*.js`, `**/*.ts`
   - Count total source files and estimate LOC

2. **Detect language and framework**
   - Check for `requirements.txt`, `Pipfile`, `pyproject.toml` → Python
   - Check for `package.json` → Node.js/JavaScript
   - Read the manifest file(s) to extract framework name and version
   - Use `Grep` to confirm framework imports in source files

3. **Detect database technology**
   - Use `Grep` to search for: `sqlite3`, `SQLAlchemy`, `psycopg2`, `pymongo`, `mysql`, `mongoose`, `sequelize`, `prisma`
   - Determine: raw SQL vs ORM, database type
   - Check if queries use parameterized placeholders (`?`, `%s`, `:param`) or string concatenation

4. **Identify the application domain**
   - Read route definitions to extract endpoint paths and resource names
   - Read model/table definitions to extract entity names
   - Classify domain: E-commerce, LMS, Task Management, CMS, etc.

5. **Assess current architecture**
   - Count files per directory
   - Check if separation directories exist: `models/`, `controllers/`, `views/`, `routes/`, `services/`
   - Classify architecture:
     - **Monolithic**: Most logic in 1-4 files, no layer separation
     - **Partially Organized**: Directories exist but responsibilities are misplaced
     - **Layered**: Clear separation of concerns across layers

6. **Print the Phase 1 summary** using this exact format:
```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      {language}
Framework:     {framework} {version}
Dependencies:  {dep1}, {dep2}, ...
Domain:        {domain_description}
Architecture:  {arch_assessment}
Source files:  {count} files analyzed
DB technology: {db_tech}
DB tables:     {table1}, {table2}, ...
================================
```

Then **immediately proceed to Phase 2** (no pause after Phase 1).

---

## PHASE 2: ARCHITECTURAL AUDIT

**Goal**: Identify all anti-patterns with exact file and line locations.

### Steps

1. **Load the anti-patterns catalog** (already loaded in the mandatory first step)

2. **Scan for each anti-pattern** in `anti-patterns-catalog.md`:
   - Use `Read` to examine each source file
   - Use `Grep` with the detection signals from the catalog
   - For each pattern found, record:
     - Severity (CRITICAL / HIGH / MEDIUM / LOW)
     - Exact file path
     - Exact line number(s)
     - What was found (specific code or pattern)
     - Why it matters
     - How to fix it

3. **Compile all findings** sorted by severity: CRITICAL → HIGH → MEDIUM → LOW

4. **Generate the audit report** using the template from `audit-report-template.md`

5. **Print the complete report**

6. **MANDATORY PAUSE**: After printing the report, you MUST print this exact line:
   ```
   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   ```
   Then **STOP and wait for user input**.
   - If user responds with `y` or `yes`: proceed to Phase 3
   - If user responds with anything else: stop execution entirely and do not modify any files

**CRITICAL RULE**: You MUST NOT modify, create, or delete any project source files before receiving user confirmation. Phase 2 is read-only.

---

## PHASE 3: REFACTORING

**Goal**: Transform the project to MVC architecture, fixing all identified issues.

### Steps

1. **Determine target structure**
   - Consult `mvc-guidelines.md` for the correct MVC structure for the detected technology
   - If the project is partially organized, adapt in-place rather than rebuilding from scratch
   - Plan the migration order before writing any files

2. **Apply transformations in this order** (order matters to avoid broken imports):
   1. Create target directory structure
   2. Create `config/settings.py` or `config/settings.js` — extract all hardcoded values to env vars
   3. Refactor/create Models — fix SQL injection, fix password handling, remove sensitive data from responses
   4. Create Controllers — extract business logic from routes/handlers
   5. Refactor Routes/Views — make them thin HTTP handlers that call controllers
   6. Create centralized error handler middleware
   7. Update entry point (app.py / app.js) as composition root
   8. Remove or archive old files that have been fully migrated

3. **Apply specific fixes** from `refactoring-playbook.md` based on findings:
   - For each CRITICAL/HIGH finding, apply the corresponding transformation pattern
   - Consult the playbook for before/after code examples in the correct language

4. **Validation**

   For Python/Flask:
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Test import
   python -c "from app import app; print('Import OK')"

   # Start server in background
   python app.py &
   SERVER_PID=$!
   sleep 3

   # Test each endpoint with curl
   curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health
   # ... test other endpoints

   # Kill server
   kill $SERVER_PID 2>/dev/null
   ```

   For Node.js/Express:
   ```bash
   # Install dependencies
   npm install

   # Start server in background
   node src/app.js &
   SERVER_PID=$!
   sleep 3

   # Test each endpoint
   curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/

   # Kill server
   kill $SERVER_PID 2>/dev/null
   ```

5. **Error recovery**: If the app fails to start:
   - Read the error output carefully
   - Diagnose the root cause (missing import, wrong path, syntax error)
   - Fix it and retry
   - Maximum 3 retry attempts before reporting failure to user

6. **Print Phase 3 summary**:
```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
{directory_tree}

Validation
  ✓/✗ Application boots without errors
  ✓/✗ GET /health (or equivalent) responds correctly
  ✓/✗ [list each tested endpoint]
  ✓/✗ Zero CRITICAL anti-patterns remaining
================================
```

---

## RULES YOU MUST NEVER BREAK

1. **Never skip loading reference files** — they contain the patterns and rules you need
2. **Never modify files in Phase 2** — it is read-only
3. **Always pause between Phase 2 and Phase 3** for user confirmation
4. **Never hardcode secrets** in refactored code — always use environment variables
5. **Always use parameterized queries** — never string concatenation in SQL
6. **Never expose passwords in API responses** — remove from serialization
7. **Always validate the app boots** after refactoring before declaring success
