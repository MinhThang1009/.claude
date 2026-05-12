# security-guidance

Senior security engineer agent for finding vulnerabilities including injection, auth flaws, insecure crypto, SSRF, XSS, and common CWEs.

## Installation

```bash
claude plugin install security-guidance@dotclaude
```

## Contents

### Agents

- `security-auditor` — Audits codebase for hardcoded secrets, injection vulnerabilities, auth flaws, insecure crypto, SSRF, XSS, and common CWEs; reports findings with severity and remediation
