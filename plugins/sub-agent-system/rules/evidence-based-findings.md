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

**Important — re-reading after Edit is not sufficient to detect state hallucination:** A sub-agent that fabricates both an Edit call and a subsequent Read call will pass this rule's check while no actual file change occurred. The only reliable verification is `git diff [file]` run by the **main agent** after receiving the sub-agent's report. Sub-agents should not self-certify edits — only the main agent can confirm via git state.
