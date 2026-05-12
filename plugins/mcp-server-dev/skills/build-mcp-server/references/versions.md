# Các phiên bản được pin

Mọi claim nhạy cảm về version trong skill này, tập trung ở một nơi. Khi cập nhật skill, kiểm tra đây trước.

| Claim | Nêu ở đâu | Lần verify cuối |
|---|---|---|
| `@modelcontextprotocol/ext-apps@1.2.2` CDN pin | `build-mcp-app/SKILL.md`, `build-mcp-app/references/widget-templates.md` (4×) | 2026-03 |
| Claude Code ≥2.1.76 cho elicitation | `elicitation.md:15`, `build-mcp-server/SKILL.md:43,76` | 2026-03 |
| MCP spec 2025-11-25 trạng thái CIMD/DCR | `auth.md:20,24,41` | 2026-03 |
| MCPB manifest schema v0.4 | `build-mcpb/references/manifest-schema.md` | 2026-03 |
| CF `agents` SDK / `McpAgent` API | `deploy-cloudflare-workers.md` | 2026-03 |
| CF template path `cloudflare/ai/demos/remote-mcp-authless` | `deploy-cloudflare-workers.md` | 2026-03 |

## Cách verify

```bash
# ext-apps mới nhất
npm view @modelcontextprotocol/ext-apps version

# CF template vẫn tồn tại
gh api repos/cloudflare/ai/contents/demos/remote-mcp-authless/src/index.ts --jq '.sha'

# MCPB schema
curl -sI https://raw.githubusercontent.com/anthropics/mcpb/main/schemas/mcpb-manifest-v0.4.schema.json | head -1
```
