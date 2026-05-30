# Evidence-Based Findings

Every finding, claim, or completion report must be grounded in direct tool output. Prevents false positives (1.1) and hallucination (4.2).

**Do:**
- Include a verbatim quote from Read or Grep output for every finding
- Re-read the changed section after every Edit to confirm the change landed
- Use the corresponding tool before claiming an action was taken (Read before "I read", Edit before "I fixed")
- Report exact file paths and line numbers taken from tool output

**Don't:**
- Flag an issue without quoting the actual code that demonstrates it
- Claim a file was edited without having called Edit on that file
- Claim a file was read without having called Read on that file
- Fabricate counts, line numbers, function names, or version numbers

If uncertain about a fact: state "unverified" rather than guessing.

## Coverage at the finding stage — don't self-filter

When a separate verification stage exists (finding-validator / pipeline-reviewer / severity-gate), a finding agent's job is **coverage, not filtering** — report every candidate issue including uncertain or low-severity ones, each tagged with a **confidence level** and **estimated severity**, and let the downstream stage rank and filter. Telling a finder to "be conservative" or "only report high-severity" drops real bugs (recall falls); surfacing a finding that later gets filtered is cheap. *(Anthropic — prompt best-practices, "Code review harnesses": "Report every issue you find... Do not filter for importance or confidence at this stage - a separate verification step will do that. Your goal here is coverage.")*

- **Single-pass self-filter** (only when there is NO downstream verifier): use a concrete bar, not vague words like "important" — report anything that could cause incorrect behavior, a test failure, or a misleading result; omit only pure style/naming nits.
- **Retract, don't assert:** after drafting findings, find a supporting quote from actual tool output for each claim. If you cannot find one, **drop the claim**. *(Anthropic — reduce-hallucinations: "If it can't find a quote, it must retract the claim.")*
- **Ground in provided sources only:** base findings on the files/data in your assigned scope and on tool output — not on general knowledge or assumptions about code you did not read. *(Anthropic — reduce-hallucinations: "only use information from provided documents and not its general knowledge.")*

**Important — re-reading after Edit is not sufficient to detect state hallucination:** A subagent that fabricates both an Edit call and a subsequent Read call will pass this rule's check while no actual file change occurred. The only reliable verification is `git diff HEAD -- [file]` run by the **main agent** after receiving the subagent's report. Sub-agents should not self-certify edits — only the main agent can confirm via git state.

## Severity Calibration (CVSS v3.1)

Use this table for consistent severity assignment across agents. When in doubt, use the higher severity.

| Severity | CVSS | Examples |
|----------|------|---------|
| 🔴 CRITICAL | 9.0–10.0 | RCE (`eval`/`exec` on **user input**), SQL injection with exfiltration, auth bypass without conditions, hardcoded production secrets |
| 🟠 HIGH | 7.0–8.9 | Stored XSS, insecure crypto (MD5/SHA1 for passwords), missing auth on sensitive endpoints (admin/delete/PII), path traversal |
| 🟡 MEDIUM | 4.0–6.9 | `eval()` on non-user input (anti-pattern), missing rate limits, PII in logs, race conditions (requires specific timing), insecure JWT config |
| 🟢 LOW | 0.1–3.9 | N+1 queries, dead code, client-side-only validation, hardcoded test keys clearly marked test-only |
| ℹ️ INFO | 0 | Code quality (function too long, nesting >3 levels), style deviations |

**Key distinctions that caused inconsistency in benchmark:**
- `eval()` on **user-controlled WebSocket/HTTP input** → 🔴 CRITICAL (RCE, unauthenticated exploit)
- `eval()` on **hardcoded string literal** → ℹ️ INFO (anti-pattern, not exploitable — FP bait pattern)
- Hardcoded secret in production config without env fallback → 🔴 CRITICAL
- Hardcoded key clearly labeled `TEST_ONLY` with no production code path → 🟢 LOW or ℹ️ INFO
