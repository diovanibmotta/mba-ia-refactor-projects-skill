# Architecture Audit Report — task-manager-api

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   13 analyzed | ~1183 lines of code

Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 5 | LOW: 6

Findings

[CRITICAL] MD5 Used for Password Hashing — Cryptographically Broken
File: models/user.py:28-32
Description: Passwords are hashed with hashlib.md5():
             self.password = hashlib.md5(pwd.encode()).hexdigest()
             check_password compares: self.password == hashlib.md5(pwd.encode()).hexdigest()
             MD5 is a fast, unsalted, collision-prone hash. Password cracking via rainbow tables
             takes milliseconds.
Impact: Full credential compromise if database is accessed. All user passwords exposed.
Recommendation: Use werkzeug.security.generate_password_hash() and check_password_hash().
                Replace set_password() and check_password() implementations.

[CRITICAL] Password Hash Exposed in All API Responses
File: models/user.py:21
Description: to_dict() method includes 'password': self.password in its return value.
             This MD5 hash is returned by: GET /users/<id> (user_routes.py:33),
             POST /users (user_routes.py:84), PUT /users/<id> (user_routes.py:128),
             POST /login (user_routes.py:209).
Impact: Every API response for user operations leaks the password hash.
Recommendation: Remove 'password' field from to_dict() entirely.

[CRITICAL] Hardcoded Email Credentials in Source Code
File: services/notification_service.py:9-10
Description: self.email_user = 'taskmanager@gmail.com' and self.email_password = 'senha123'
             are plaintext credentials committed to source code.
Impact: Email account compromise. Cannot rotate without code changes.
Recommendation: Extract to environment variables. NotificationService should read from config.

[CRITICAL] Hardcoded Secret Key
File: app.py:13
Description: app.config['SECRET_KEY'] = 'super-secret-key-123'
             Literal secret key committed to source code.
Impact: Session tokens can be forged. Any attacker with source access can impersonate any user.
Recommendation: SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-in-production')

[HIGH] Overdue Check Logic Duplicated in 6 Places — Existing is_overdue() Never Called
File: routes/task_routes.py:30-38,69-78,280-284 | routes/user_routes.py:170-179 | routes/report_routes.py:33-43,132-135
Description: The overdue check logic is copy-pasted 6 times across 3 route files:
               if t.due_date and t.due_date < datetime.utcnow() and t.status not in ['done','cancelled']:
             Task.is_overdue() method (task.py:50-60) exists but is NEVER called anywhere.
             Additionally, is_overdue() has a syntax error (misaligned indentation on line 53).
Impact: Bug fixes must be applied in 6 places. Current overdue logic diverges from is_overdue().
Recommendation: Fix is_overdue() syntax error. Call task.is_overdue() everywhere instead.

[HIGH] Status and Priority Validation Duplicated — Existing Model Methods Never Called
File: routes/task_routes.py:108-112, 174-180
Description: Task.validate_status() (task.py:38-43) and Task.validate_priority() (task.py:45-48) exist
             but are NEVER called. Inline validation is duplicated in create_task and update_task:
               if status not in ['pending', 'in_progress', 'done', 'cancelled']:
               if priority < 1 or priority > 5:
Impact: Model's canonical validation is bypassed. Any change requires updating 2+ locations.
Recommendation: Call task.validate_status() and task.validate_priority() in controller layer.

[HIGH] Category CRUD Placed in Report Blueprint
File: routes/report_routes.py:157-223
Description: Full Category CRUD (GET /categories, POST /categories, PUT /categories/<id>,
             DELETE /categories/<id>) is implemented in report_routes.py which handles reporting.
             These are unrelated concerns sharing a blueprint.
Impact: Violates Single Responsibility. Navigation and discoverability are poor.
Recommendation: Extract to routes/category_routes.py with its own blueprint.

[HIGH] No Controller Layer — All Business Logic in Routes
File: routes/task_routes.py, routes/user_routes.py, routes/report_routes.py
Description: All business logic (validation, orchestration, DB queries) is directly in route
             handlers. No controllers/ directory exists. Email regex is duplicated between
             user_routes.py lines 61 and 105. services/notification_service.py is never imported.
Impact: Routes are 20-60+ lines each. Cannot test business rules without HTTP layer.
Recommendation: Create controllers/ layer. Extract logic from routes. Call controllers from routes.

[HIGH] Debug Mode and 0.0.0.0 Binding Hardcoded
File: app.py:34
Description: app.run(debug=True, host='0.0.0.0', port=5000) — all hardcoded.
             Werkzeug debugger exposes arbitrary code execution to all network interfaces.
Impact: In any environment where this code runs on a server, the interactive debugger is exposed.
Recommendation: Extract to environment variables. Use host='127.0.0.1' as default.

[MEDIUM] N+1 Query Problem in Task List
File: routes/task_routes.py:40-55
Description: For each task in get_tasks(), two additional queries are executed:
             - User.query.get(t.user_id) (line 41)
             - Category.query.get(t.category_id) (line 49)
             With 100 tasks: 201 queries instead of 1 with eager loading.
Impact: Response time grows linearly with task count.
Recommendation: Use SQLAlchemy eager loading:
                Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()

[MEDIUM] N+1 Query Problem in Summary Report
File: routes/report_routes.py:53-68
Description: summary_report() executes one query per user to get their tasks:
             user_tasks = Task.query.filter_by(user_id=u.id).all() inside a for loop.
             With 100 users: 101 queries instead of a single GROUP BY query.
Impact: Report endpoint becomes slower with each user added.
Recommendation: Use db.session.query(User, func.count(Task.id)).outerjoin(Task).group_by(User.id)

[MEDIUM] Deprecated datetime.utcnow() Usage
File: models/user.py:14 | models/task.py:15-16,52 | models/category.py:11 | routes/task_routes.py:31,70,212,282 | routes/user_routes.py:171 | routes/report_routes.py:35,133
Description: datetime.utcnow() is deprecated since Python 3.12.
             Used in 10+ locations across models and routes.
Impact: Will emit DeprecationWarning in Python 3.12+. Will break in future Python versions.
Recommendation: Replace with datetime.now(timezone.utc) and update column defaults.

[MEDIUM] Bare except Clauses Throughout Routes
File: routes/task_routes.py:60,135,201,233 | routes/report_routes.py:186,208,222 | routes/user_routes.py:129,149 | utils/helpers.py:45,48
Description: Multiple bare except: clauses catch all exceptions including KeyboardInterrupt
             and SystemExit. Errors are silently swallowed or generic messages returned.
Impact: Bugs are hidden. Debugging is nearly impossible. Critical errors may be masked.
Recommendation: Catch specific exceptions: except Exception as e:
                Use centralized error handler for unhandled exceptions.

[MEDIUM] Dead Code — Unused Imports and Utility Functions
File: app.py:7 | routes/task_routes.py:7 | utils/helpers.py:3-7
Description: - app.py:7 imports os, sys, json, datetime — only datetime is used
             - task_routes.py:7 imports json, os, sys, time — none are used
             - utils/helpers.py imports os, json, sys, math, hashlib — none are used
             - utils/helpers.py defines process_task_data() which is never called
             - services/notification_service.py is never imported anywhere
             - requirements.txt lists marshmallow and requests which are never used
Impact: Code bloat. Confusion about what is actually in use.
Recommendation: Remove unused imports. Wire up notification_service or delete it.

[LOW] Syntax Error in Task.is_overdue() Method
File: models/task.py:52-53
Description: is_overdue() has a misaligned if statement:
             Line 52: if self.due_date < datetime.utcnow():
             Line 53: if self.status != 'done' ...  (same indent as line 52, should be nested)
             This is a bug — the method's logic is incorrect as written.
Impact: is_overdue() would never be callable without a syntax error.
Recommendation: Fix indentation to properly nest the status check inside the date check.

[LOW] Fake JWT Token in Login Response
File: routes/user_routes.py:210
Description: 'token': 'fake-jwt-token-' + str(user.id) — not a real authentication token.
             There is no token validation anywhere in the codebase.
Impact: Any caller can construct a "token" for any user_id without ever logging in.
Recommendation: Implement real JWT using PyJWT, or at minimum remove the fake token.

[LOW] Duplicate Login Query
File: routes/user_routes.py:196-200
Description: User.query.filter_by(email=email).first() is called twice in sequence (lines 196 and 200).
             The result of the first call is checked, then the exact same query runs again.
Impact: Unnecessary database query on every login attempt.
Recommendation: Remove the duplicate query at line 200. Use the result from line 196.

[LOW] Verbose Boolean Returns
File: models/task.py:38-43,45-48,50-60 | models/user.py:34-38 | utils/helpers.py:20-22,52-54
Description: Multiple methods use verbose if/return True/else/return False patterns
             instead of direct boolean expressions.
             Example: return new_status in valid (instead of if/True/else/False)
Impact: Extra noise, harder to read.
Recommendation: return new_status in valid; return 1 <= p <= 5; return bool(re.match(...))

[LOW] CORS Wildcard — No Origin Restriction
File: app.py:15
Description: CORS(app) with no origin restriction.
Recommendation: CORS(app, origins=os.environ.get('CORS_ORIGINS', '*').split(','))

================================
Total: 20 findings
================================
```
