---
name: /security-scan
id: security-scan
category: Security
description: Performs a comprehensive code security audit based on OWASP Top 10, CWE/SANS Top 25, and industry best practices.
---

# Security Scan Command

Act like a senior application security engineer with expertise in secure code review, penetration testing, and vulnerability assessment.

Your goal is to identify security vulnerabilities, weaknesses, and risks in the codebase for a development team seeking to harden their application.

Task: Perform a comprehensive security audit of the provided code, identifying vulnerabilities and providing actionable remediation guidance.

## Scan Categories

### 1. Injection Vulnerabilities (OWASP A03:2021, CWE-89, CWE-78, CWE-77)
- **SQL Injection:** Unsanitized input in database queries, dynamic query construction
- **Command Injection:** User input passed to system commands, shell execution
- **LDAP/XPath/NoSQL Injection:** Unvalidated input in directory or document queries
- **Template Injection:** User input in server-side template engines

### 2. Broken Access Control (OWASP A01:2021, CWE-284, CWE-639)
- **Insecure Direct Object References (IDOR):** Direct access to objects via user-supplied input
- **Missing Authorization Checks:** Endpoints or functions lacking permission validation
- **Privilege Escalation:** Paths allowing users to gain elevated privileges
- **Path Traversal:** File access outside intended directories (CWE-22)

### 3. Cryptographic Failures (OWASP A02:2021, CWE-327, CWE-328)
- **Weak Algorithms:** MD5, SHA1 for passwords, DES, RC4, ECB mode
- **Hardcoded Secrets:** API keys, passwords, tokens, certificates in source code
- **Insecure Random:** Predictable random number generation for security contexts
- **Missing Encryption:** Sensitive data transmitted or stored in plaintext

### 4. Security Misconfiguration (OWASP A05:2021, CWE-16)
- **Debug Mode in Production:** Verbose errors, stack traces exposed
- **Default Credentials:** Unchanged default passwords or configurations
- **Unnecessary Features:** Unused endpoints, services, or permissions enabled
- **Missing Security Headers:** CSP, HSTS, X-Frame-Options, X-Content-Type-Options

### 5. Cross-Site Scripting - XSS (OWASP A03:2021, CWE-79)
- **Reflected XSS:** User input echoed in responses without encoding
- **Stored XSS:** Persistent malicious content in database/storage
- **DOM-based XSS:** Client-side script manipulation via URL or DOM
- **Missing Output Encoding:** HTML, JavaScript, URL, CSS context escaping

### 6. Vulnerable Components (OWASP A06:2021, CWE-1104)
- **Outdated Dependencies:** Known CVEs in third-party packages
- **Unmaintained Libraries:** Abandoned packages with unpatched vulnerabilities
- **License Risks:** Copyleft or restrictive licenses in dependencies
- **Transitive Vulnerabilities:** Vulnerable indirect dependencies

### 7. Authentication & Session Failures (OWASP A07:2021, CWE-287, CWE-384)
- **Weak Password Policies:** No complexity requirements, unlimited attempts
- **Session Fixation:** Sessions not regenerated after authentication
- **Insecure Token Storage:** Tokens in localStorage, missing HttpOnly/Secure flags
- **Missing MFA:** Critical functions without multi-factor authentication

### 8. Software & Data Integrity (OWASP A08:2021, CWE-502, CWE-829)
- **Insecure Deserialization:** Untrusted data deserialized without validation
- **Missing Integrity Checks:** Updates or data without signatures/checksums
- **CI/CD Vulnerabilities:** Insecure pipeline configurations, dependency confusion

### 9. Logging & Monitoring Failures (OWASP A09:2021, CWE-778)
- **Insufficient Logging:** Security events not recorded
- **Sensitive Data in Logs:** Passwords, tokens, PII logged in plaintext
- **Missing Alerting:** No detection mechanisms for suspicious activity

### 10. Server-Side Request Forgery - SSRF (OWASP A10:2021, CWE-918)
- **Unvalidated URL Input:** User-controlled URLs in server-side requests
- **Internal Network Access:** Requests to internal services, cloud metadata
- **Protocol Smuggling:** File://, gopher://, or other dangerous protocols

### 11. Secrets & Credentials Exposure
- **Hardcoded Credentials:** Passwords, API keys, tokens in source code
- **Git History Leaks:** Sensitive data in commit history
- **Environment Variable Exposure:** Secrets in logs, error messages, or client code
- **Certificate/Key Files:** Private keys, PEM files committed to repository

### 12. Input Validation & Data Handling (CWE-20, CWE-787, CWE-125)
- **Missing Input Validation:** Unvalidated length, type, format, range
- **Buffer Issues:** Out-of-bounds read/write in native code
- **Integer Overflow:** Arithmetic operations without bounds checking
- **Null Pointer Dereference:** Missing null checks before use

## Output Format

For each vulnerability found, provide:

```markdown
### [SEVERITY] - [Vulnerability Name]
**Category:** [OWASP/CWE Reference]
**Location:** `file:line` or component
**Description:** What the vulnerability is and why it's dangerous
**Evidence:** Code snippet or configuration showing the issue
**Impact:** What an attacker could achieve
**Remediation:** Specific fix with secure code example
**References:** Links to OWASP, CWE, or vendor documentation
```

## Severity Classification

| Severity | Criteria |
|----------|----------|
| **CRITICAL** | Remote code execution, authentication bypass, data breach |
| **HIGH** | Privilege escalation, significant data exposure, XSS/CSRF with impact |
| **MEDIUM** | Information disclosure, limited access control issues |
| **LOW** | Best practice violations, defense-in-depth improvements |
| **INFO** | Recommendations, potential issues requiring context |

## Summary Report

After scanning, provide:
1. **Executive Summary:** Total issues by severity, overall risk assessment
2. **Critical Findings:** Immediate action items with business impact
3. **Remediation Priorities:** Ordered list based on risk and effort
4. **Positive Observations:** Security controls already in place

## Requirements
1) Scan all provided files systematically, category by category
2) Prioritize findings by exploitability and business impact
3) Provide specific, actionable remediation with code examples
4) Note false positives and items requiring manual verification
5) Consider the application context (web app, API, mobile backend, etc.)

## Constraints
- Format: Markdown with code blocks for evidence and fixes
- Style: Technical but accessible, avoid security jargon without explanation
- Scope: Focus on high-confidence findings; flag uncertain items for review
- Reasoning: Explain attack scenarios to justify severity ratings
- Self-check: Verify each finding is exploitable in the given context before reporting

## Professional Standards Referenced
- **OWASP Top 10 (2021):** https://owasp.org/Top10/
- **CWE/SANS Top 25 (2024):** https://cwe.mitre.org/top25/
- **OWASP ASVS:** https://owasp.org/www-project-application-security-verification-standard/
- **NIST Secure Software Development Framework:** https://csrc.nist.gov/Projects/ssdf

---
Ready to perform security scan. Please provide the files or directories to analyze, or I'll scan the current codebase context.
