# Architecture Audit Report — ecommerce-api-legacy

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express
Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 5 | LOW: 6

Findings

[CRITICAL] Hardcoded Live Credentials and API Keys
File: src/utils.js:2-4
Description: Three production credentials hardcoded as string literals:
             - dbPass: "senha_super_secreta_prod_123"
             - paymentGatewayKey: "pk_live_1234567890abcdef" (live payment gateway key)
             - smtpUser: "no-reply@fullcycle.com.br" (email credential)
             These are committed to source code and visible to anyone with repo access.
Impact: Payment gateway key exposes financial operations. Email credentials enable phishing.
        Cannot be rotated without code changes.
Recommendation: Move all to environment variables: process.env.PAYMENT_GATEWAY_KEY, etc.
                Add .env to .gitignore. Provide .env.example with dummy values.

[CRITICAL] Credit Card Number and API Key Logged to Console
File: src/AppManager.js:45
Description: console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`)
             Both the full credit card number and the live payment gateway key are printed
             to stdout on every checkout attempt.
Impact: PCI-DSS violation. Credit card numbers in server logs constitute a severe compliance
        failure. Any log aggregation system, monitoring tool, or log file becomes a data breach.
Recommendation: Remove this log line entirely. If logging is needed: console.log("Processing payment")

[CRITICAL] Fake / Insecure Password Hashing
File: src/utils.js:17-23
Description: badCrypto() function performs 10,000 iterations of Base64 encoding and truncates
             to 10 characters. Base64 is encoding, not hashing — it is trivially reversible.
             This is not a password hashing algorithm. Users created via checkout use badCrypto().
             The seed user (AppManager.js:18) has plaintext password '123'.
Impact: All stored "hashes" can be decoded instantly. Full credential compromise if DB is accessed.
Recommendation: Use bcrypt: const bcrypt = require('bcrypt'); bcrypt.hashSync(pwd, 10)
                Add bcrypt to package.json dependencies.

[CRITICAL] No Authentication on Admin Financial Report Endpoint
File: src/AppManager.js:80
Description: GET /api/admin/financial-report is publicly accessible with no authentication.
             Returns all course revenue, student names, and payment data.
Impact: Complete financial data exposure to any unauthenticated caller on the internet.
Recommendation: Add authentication middleware. At minimum, require an admin API key header.

[HIGH] God Class — AppManager
File: src/AppManager.js:4-139
Description: Single class contains: database schema creation, seed data insertion, route
             registration, checkout business logic, payment processing, financial reporting,
             user deletion, and audit logging. 139 lines, 3 public methods, all responsibilities mixed.
             Violates Single Responsibility Principle.
Impact: Untestable. Any change to one concern risks breaking others. Cannot be worked on
        by multiple developers simultaneously.
Recommendation: Decompose into: models/ (DB access), controllers/ (business logic), routes/ (HTTP).
                Apply God Class Decomposition pattern from the refactoring playbook.

[HIGH] N+1+1 Query Problem in Financial Report
File: src/AppManager.js:83-128
Description: The report endpoint executes queries at 4 nesting levels:
             1. SELECT * FROM courses (1 query)
             2. For each course: SELECT * FROM enrollments WHERE course_id = ? (N queries)
             3. For each enrollment: SELECT name FROM users WHERE id = ? (N*M queries)
             4. For each enrollment: SELECT amount FROM payments WHERE enrollment_id = ? (N*M queries)
             With 10 courses and 5 students each: 111 queries instead of 2.
Impact: Response time grows with O(N*M) complexity. Will timeout at scale.
Recommendation: Replace with a single JOIN query across all 4 tables.

[HIGH] Callback Hell — 5 Levels of Nesting in Checkout
File: src/AppManager.js:37-77
Description: The checkout handler nests callbacks 5 levels deep: course query → user lookup
             → user creation → enrollment insert → payment insert → audit log insert.
             Manual async coordination with nested function definitions.
Impact: Code is extremely hard to read, debug, or extend. Error handling is incomplete
        (audit log error on line 57-58 is silently ignored).
Recommendation: Convert to async/await using promisified sqlite3 calls.

[HIGH] Orphaned Data on User Deletion
File: src/AppManager.js:131-137
Description: DELETE /api/users/:id deletes the user row but leaves enrollments, payments, and
             audit logs referencing that user_id. The response acknowledges this explicitly:
             "as matrículas e pagamentos ficaram sujos no banco."
             No cascade delete, no cleanup logic.
Impact: Database integrity violation. Orphaned payment records. Broken foreign key references.
Recommendation: Delete related records in a transaction before deleting the user, or use
                CASCADE DELETE foreign key constraints.

[MEDIUM] No Input Validation on Checkout
File: src/AppManager.js:29-35
Description: Only presence check for usr, eml, c_id, cc. No validation of:
             - Email format
             - Card number format (any string starting with "4" is "PAID")
             - Course ID type (should be integer)
             - Password strength
Impact: Malformed data enters the database. Fake "payments" with invalid cards.
Recommendation: Add input validation middleware or inline validation with meaningful error messages.

[MEDIUM] Terrible Variable Naming
File: src/AppManager.js:29-33
Description: Single-letter and cryptic variable names:
             - u (should be name/userName)
             - e (should be email)
             - p (should be password)
             - cid (should be courseId)
             - cc (should be cardNumber)
             - c (line 89, should be course)
             - enr (line 102, should be enrollment)
Impact: Code is unreadable. Maintenance requires decoding variable names.
Recommendation: Use descriptive names: const { usr: name, eml: email, c_id: courseId, card: cardNumber }

[MEDIUM] Magic Number for Payment Logic
File: src/AppManager.js:46
Description: Payment approval is determined by: cc.startsWith("4")
             The string "4" is a magic constant with no documentation. It represents the Visa
             card number prefix, used as a mock payment gateway.
Impact: Business rule is invisible in code. Anyone maintaining the code cannot understand it.
Recommendation: const VISA_PREFIX = "4"; or better, replace with a real payment gateway integration.

[MEDIUM] Silent Error Swallowing
File: src/AppManager.js:57-58, 133-136
Description: - Audit log insert callback (line 57) receives err but never checks it.
               If the insert fails, execution continues and a success response is sent.
             - User delete callback (line 133) receives err but never checks it.
               Database errors during deletion are silently ignored.
Impact: Failures are undetectable. Data inconsistencies occur with no notification.
Recommendation: Always check err in callbacks. Use next(err) to propagate to error handler.

[MEDIUM] SELECT * Over-fetching
File: src/AppManager.js:37,83
Description: SELECT * FROM courses WHERE id = ? and SELECT * FROM courses fetch all columns.
             Only specific columns are used in each case.
Impact: Unnecessary data transfer. Performance overhead increases with schema growth.
Recommendation: Specify required columns: SELECT id, title, price FROM courses

[LOW] No CORS Configuration
File: src/app.js
Description: No CORS middleware is configured. Cross-origin behavior is browser-default.
Recommendation: Add cors package: app.use(cors({ origin: process.env.ALLOWED_ORIGINS }))

[LOW] No Security Headers
File: src/app.js
Description: No Helmet or equivalent security headers middleware.
Impact: Missing X-Frame-Options, CSP, X-XSS-Protection headers.
Recommendation: npm install helmet; app.use(require('helmet')())

[LOW] self = this Legacy Pattern
File: src/AppManager.js:26
Description: const self = this is a pre-ES6 workaround for 'this' binding in callbacks.
             Unnecessary with arrow functions or async/await.
Recommendation: Use arrow functions () => {} or async/await to eliminate self.

[LOW] Exported but Unused totalRevenue
File: src/utils.js:10,25
Description: let totalRevenue = 0 is exported but never read or modified anywhere in the codebase.
Recommendation: Delete the variable and remove from exports.

[LOW] Inconsistent HTTP Response Format
File: src/AppManager.js:35,60,135
Description: Some responses are plain text (res.send("Bad Request")), others are JSON
             (res.json({msg: "Sucesso"})). No standardized response envelope.
Recommendation: Always respond with JSON: res.status(400).json({ error: "Bad Request" })

[LOW] Seed User with Plaintext Password
File: src/AppManager.js:18
Description: INSERT INTO users ... VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')
             The seed user has plaintext password '123', not even using the (bad) badCrypto function.
Recommendation: Hash seed passwords with bcrypt before insertion.

================================
Total: 19 findings
================================
```
