# Task Dependency

Identify dependencies before spawning agents and pass outputs explicitly between dependent phases. Prevents context loss (2.2) and out-of-order execution (2.3).

**Do:**
- Map which tasks depend on outputs from other tasks before spawning anything
- Wait for dependency COMPLETION status before spawning any dependent task
- Pass dependency outputs explicitly in the dependent agent's prompt — sub-agents start with fresh context and do not see previous results
- Use the context-packager skill to compress relevant context before injecting it

**Don't:**
- Spawn a dependent task before its dependency has completed and been verified
- Assume a sub-agent will infer what happened in a prior phase without being told

**Template for injecting dependency context:**

```
Context from previous phase:
- [Key finding or change from Task A]
- [Interface or API changes the next agent must know]

Your task: [Task B description]
```
