---
name: explain
description: "Explains code, algorithms, or architecture to those unfamiliar with it. Goes from overview to details with concrete examples. Use when user says 'explain', 'what does this do', or 'why does this work'."
allowed-tools: Read Grep Glob Bash(git log:*) Bash(git blame:*) WebFetch WebSearch
argument-hint: [file path, function/class name, or question]
---

# Skill: Explain code

You are called to explain code/algorithms/concepts to the user. Goal: the user understands **why** the code works the way it does, not just *what* it does.

## Step 1: Identify the subject

Depending on `$ARGUMENTS`:
- File path → explain that file
- Function/class/symbol name → find with Grep, explain it
- Open-ended question ("how does the auth system work") → explore the codebase, synthesize

## Step 2: Read enough context

Do NOT read 1 file and then explain. Minimum:
- The main file
- Callers of this file/function (Grep the function name in the codebase)
- Related types/interfaces
- Corresponding tests (tests are often the best living documentation)
- Git log for the file → is there any important historical context?

## Step 3: Structure the explanation

Follow the **inverted pyramid** model (top-down):

### 1. One-sentence summary
"This code does X by doing Y."

### 2. The big picture (3-5 sentences)
- Where does it live in the system?
- Who calls it? What does it call?
- When does it run? How often?

### 3. Go into the details
- Walk through each important part
- Each code block gets a short note on **WHY**, not repeating WHAT
- Flag anything confusing or counter-intuitive

### 4. Concrete examples
- For a specific input, trace through the code — what is the output?
- Edge cases: empty input, large input, invalid input → behavior?

### 5. Pitfalls & gotchas
- Are there any places that are easy to misunderstand?
- Are there any implicit assumptions?
- Are there any related TODO/FIXME items?

## Step 4: Format

Depending on explanation length:

**Short (< 5 sentences)**: write plain prose, no headings needed.

**Medium (5-15 sentences)**: use bullets or 2-3 clear paragraphs.

**Long (> 15 sentences or architectural explanation)**: use headings, for example:

```markdown
## TL;DR
[1-2 sentences]

## Big picture
[Diagram if possible — use ASCII art or Mermaid]

## Details
### Part A: [name]
...

### Part B: [name]
...

## Trace example
Input: ...
Output: ...
[step-by-step]

## Notes
- ...
```

## Rules

- **Use language appropriate for the user**. If the user is a junior, avoid unexplained jargon. If the user is a senior, move quickly.
- **Do not fabricate**. If there is an uncertain part in the code → read more or say outright "this part needs verification". Do NOT guess "it probably does X".
- **Link to sources**: link to specific file:line, or PR/commit if information comes from git history.
- **Compare to familiar patterns**: "This is the Observer pattern", "Structure is like Express middleware". Helps user map to existing knowledge.
- **Do not lecture**. Explain only what was asked, do not narrate the history of the language.

## When user asks "why is the code written this way"

This is a question about intent:
1. Read `git blame` to find the original commit.
2. Read the commit message and PR description (if any).
3. If nothing is found → say outright "there is no historical documentation for this decision; here are some *technical* reasons that may apply based on the code:".
4. List 2-3 hypotheses, clearly marked as "this is inference, not confirmed".

## When user asks about an algorithm/concept not present in the code

(e.g., "explain Bloom filter", "explain React reconciliation")

- Answer from existing knowledge.
- If it relates to a new framework/library (< 1 year old) → WebSearch to confirm version-specific behavior.
- Provide illustrative examples using pseudo-code or short code.
- Point to official sources (docs, paper) if the user wants to go deeper.
