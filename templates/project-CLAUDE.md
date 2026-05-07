# <TÊN PROJECT>

> File này load mọi session khi làm project này. Cộng dồn với `~/.claude/CLAUDE.md` global. Chỉ chứa thứ RIÊNG project, KHÔNG lặp lại global. Giữ <80 dòng.

## Mô tả project

<1-2 câu: project này làm gì, dùng cho ai, ở stage nào (MVP / production / maintenance).>

## Tech stack

- **Language**: <vd: TypeScript 5.x, Python 3.12, Go 1.22>
- **Framework**: <vd: Next.js 14 / NestJS / FastAPI / Spring Boot>
- **Database**: <vd: PostgreSQL 16, Redis 7>
- **Test**: <vd: Vitest, pytest, Go test>
- **Build**: <vd: Vite, esbuild, Maven>
- **Deploy**: <vd: Vercel, AWS ECS, GCP Cloud Run>

## Lệnh quan trọng

```bash
<command-cài-deps>           # vd: pnpm install
<command-dev>                 # vd: pnpm dev
<command-test>                # vd: pnpm test
<command-test-watch>          # vd: pnpm test:watch
<command-lint>                # vd: pnpm lint
<command-typecheck>           # vd: pnpm typecheck
<command-format>              # vd: pnpm format
<command-build>               # vd: pnpm build
<command-migrate-db>          # vd: pnpm db:migrate
```

## Cấu trúc thư mục

```text
src/
├── <module-1>/   # mô tả ngắn
├── <module-2>/   # mô tả ngắn
└── ...
tests/
docs/
```

<Chỉ note thư mục có quy ước SPECIAL — không list từng folder.>

## Convention RIÊNG project

<Chỉ ghi những convention KHÁC global, hoặc cụ thể project này. Vd:>
- Tất cả API endpoint trả về `{ data, error, meta }`, không bare object.
- Tên file React component: `PascalCase.tsx`. Hook: `useCamelCase.ts`.
- DB column: `snake_case`. JS variable: `camelCase`. Model class: `PascalCase`.
- Tất cả `useState` cho async data → dùng React Query thay thế.

## Module owner & nơi cần cẩn thận

- `src/auth/*` — security sensitive, cần test trước khi sửa.
- `src/payment/*` — KHÔNG sửa khi không có ticket. Chạm code này phải có review @<owner>.
- `src/migration/*` — chỉ thêm migration mới, KHÔNG sửa migration cũ đã apply.

## Vùng cấm / điều cần biết

- KHÔNG đổi schema DB không có migration file kèm.
- KHÔNG `git push --force` lên `main`/`develop`.
- KHÔNG bypass pre-commit hook (lint/test phải pass).
- API breaking change phải bump major version + cập nhật `CHANGELOG.md`.

## Compact Instructions (cho `/compact` cả manual và auto)

Khi compact, summary PHẢI giữ:
1. **File đã sửa** trong session (full path) + lý do từng file.
2. **Migration đã chạy** / dependency đã thêm.
3. **Quyết định kiến trúc** đã chốt (kèm rationale 1 câu).
4. **Bước đang dở** + bước tiếp theo cụ thể.
5. **Bug đã reproduce** nhưng chưa fix.
Bỏ qua: tool output dài, build log, dead-end debugging.

## Tham chiếu

- Docs project: <link Notion / Confluence / Wiki>
- Design system: <link Figma>
- API spec: <link Swagger / Postman>
- Deployment runbook: <link>
