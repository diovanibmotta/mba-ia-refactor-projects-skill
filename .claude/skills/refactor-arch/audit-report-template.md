# Audit Report Template

Use this template to format the Phase 2 audit report. Fill in all placeholders with actual findings.

---

## Report Format

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: {project_directory_name}
Stack:   {Language} + {Framework}
Files:   {N} analyzed | ~{LOC} lines of code

Summary
CRITICAL: {n} | HIGH: {n} | MEDIUM: {n} | LOW: {n}

Findings

[CRITICAL] {Finding Title}
File: {relative/path/to/file.ext}:{start_line}-{end_line}
Description: {What exactly was found — be specific, include the offending code snippet}
Impact: {Why this is dangerous or harmful}
Recommendation: {Concrete fix — what to change and how}

[CRITICAL] {Next Finding Title}
File: {relative/path/to/file.ext}:{line}
Description: {Description}
Impact: {Impact}
Recommendation: {Recommendation}

[HIGH] {Finding Title}
File: {relative/path/to/file.ext}:{start_line}-{end_line}
Description: {Description}
Impact: {Impact}
Recommendation: {Recommendation}

[MEDIUM] {Finding Title}
File: {relative/path/to/file.ext}:{start_line}-{end_line}
Description: {Description}
Impact: {Impact}
Recommendation: {Recommendation}

[LOW] {Finding Title}
File: {relative/path/to/file.ext}:{line}
Description: {Description}
Impact: {Impact}
Recommendation: {Recommendation}

================================
Total: {total_count} findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Field Definitions

**Project**: The name of the directory being analyzed (e.g., `code-smells-project`)

**Stack**: Language + Framework (e.g., `Python + Flask`, `JavaScript + Express`)

**Files**: Number of source files analyzed + approximate total lines of code

**Summary line**: Count of findings per severity level, all on one line

**Finding Title**: Short, descriptive name for the pattern found (e.g., "SQL Injection via String Concatenation", "Hardcoded SECRET_KEY")

**File**: Relative path from project root + line number(s). Use range `start-end` for multi-line issues. Use single line `:N` for point issues.

**Description**: What was found. Be specific — include the variable name, function name, or the actual offending code snippet. Do NOT be generic like "there is a security problem". Say "The `login_usuario` function at line 109 builds the WHERE clause by concatenating the `email` parameter directly: `... WHERE email = '" + email + "'`".

**Impact**: Concrete harm. What an attacker could do, or what maintenance problem this causes.

**Recommendation**: Actionable fix. Name the specific function, library, or pattern to use.

---

## Ordering Rules

1. Sort ALL findings by severity: CRITICAL first, then HIGH, MEDIUM, LOW
2. Within the same severity, order by file (alphabetical) then by line number
3. Number each finding sequentially (optional but helpful for large reports)

---

## Example Finding

```
[CRITICAL] SQL Injection via String Concatenation
File: models.py:109-110
Description: The `login_usuario` function builds the authentication query by directly
             concatenating the `email` and `senha` parameters:
             `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`
             Any attacker can log in as admin with email: `admin@loja.com' OR '1'='1' --`
Impact: Complete authentication bypass. Any user can log in as any other user without
        knowing their password.
Recommendation: Replace with parameterized query:
                cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
```

---

## Confirmation Prompt

After printing the complete report and total count, always end with this exact line:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Then STOP and wait for user input before doing anything else.
