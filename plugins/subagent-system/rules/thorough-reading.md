# Thorough Reading

Read the complete file before drawing conclusions. Prevents incomplete analysis (4.1).

**Do:**
- Read the entire assigned file before reporting findings or conclusions
- For files over 500 lines, use Read with offset and limit to process in chunks
- Report the line ranges read at each chunk: "Read lines X–Y: [summary]"
- Summarize each chunk before moving to the next

**Don't:**
- Conclude "no issues found" without having read the entire file
- Assume a section not yet read is clean

**Chunked reading protocol for files over 500 lines:**

```
Read(offset=0,   limit=200) → summarize chunk 1
Read(offset=200, limit=200) → summarize chunk 2
Read(offset=400, limit=200) → summarize chunk 3
... continue until end of file
```

Each chunk summary must be written before requesting the next chunk. Never skip a chunk based on assumptions about its content.
