# Thorough Reading

Read the complete file before drawing conclusions. Prevents incomplete analysis (4.1).

**Do:**
- Read the entire assigned file before reporting findings or conclusions
- Read the file in one pass when the whole file fits in a single read; only when the file exceeds one Read call (Read returns ~2000 lines per call, then truncates) use offset and limit to process in chunks — overlap chunks so a definition and its use aren't split across the boundary
- Report the line ranges read at each chunk: "Read lines X–Y: [summary]"
- Summarize each chunk before moving to the next

**Don't:**
- Conclude "no issues found" without having read the entire file
- Assume a section not yet read is clean

**Chunked reading protocol for files that exceed one Read call (~2000 lines):**

```
Read(offset=0,   limit=500) → summarize chunk 1
Read(offset=450, limit=500) → summarize chunk 2  (overlaps prior chunk by ~50 lines)
Read(offset=900, limit=500) → summarize chunk 3  (overlaps prior chunk by ~50 lines)
... continue until end of file
```

Each chunk summary must be written before requesting the next chunk. Never skip a chunk based on assumptions about its content.
