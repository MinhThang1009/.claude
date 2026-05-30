# File Ownership

Before spawning parallel agents, assign a non-overlapping file set to each agent. Prevents scope overlap and race conditions.

**Do:**
- Assign a disjoint file set to every parallel agent before spawning
- Document ownership explicitly: `Agent A → [files]`, `Agent B → [files]`
- Partition by file or directory ownership
- After a batch completes, compare file lists from each agent's report — if the same file appears in two agents' outputs, merge by keeping the higher-severity finding

**Don't:**
- Spawn two agents that may edit the same file simultaneously
- Partition by concern type (e.g., "Agent A does security review of all src/", "Agent B does performance review of all src/") — this guarantees overlap

**Correct partition:**
```
Agent A: src/auth/, src/middleware/
Agent B: src/api/, src/services/
```

**Incorrect partition:**
```
Agent A: security review of entire src/
Agent B: performance review of entire src/
```
