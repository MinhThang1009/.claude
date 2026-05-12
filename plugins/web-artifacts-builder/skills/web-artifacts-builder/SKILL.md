---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

Để build các claude.ai artifact frontend mạnh mẽ, làm theo các bước sau:
1. Khởi tạo frontend repo bằng `scripts/init-artifact.sh`
2. Phát triển artifact bằng cách sửa code đã generate
3. Bundle toàn bộ code vào một file HTML duy nhất bằng `scripts/bundle-artifact.sh`
4. Hiển thị artifact cho user
5. (Tùy chọn) Test artifact

**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui

## Hướng dẫn Design & Style

RẤT QUAN TRỌNG: Để tránh hiện tượng thường gọi là "AI slop", tránh dùng layout centered quá nhiều, gradient tím, bo góc đồng đều, và font Inter.

## Quick Start

### Bước 1: Khởi tạo Project

Chạy script khởi tạo để tạo React project mới:
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

Lệnh này tạo một project được cấu hình đầy đủ với:
- ✅ React + TypeScript (qua Vite)
- ✅ Tailwind CSS 3.4.1 với hệ thống theming shadcn/ui
- ✅ Path alias (`@/`) đã cấu hình
- ✅ 40+ shadcn/ui component đã pre-install
- ✅ Toàn bộ Radix UI dependency
- ✅ Parcel đã cấu hình để bundle (qua .parcelrc)
- ✅ Tương thích Node 18+ (tự detect và pin version Vite)

### Bước 2: Phát triển Artifact

Để build artifact, sửa các file đã được generate. Xem **Common Development Tasks** bên dưới để được hướng dẫn.

### Bước 3: Bundle thành file HTML duy nhất

Để bundle React app thành một HTML artifact duy nhất:
```bash
bash scripts/bundle-artifact.sh
```

Lệnh này tạo `bundle.html` - một artifact self-contained với toàn bộ JavaScript, CSS, và dependency được inline. File này có thể share trực tiếp trong cuộc trò chuyện Claude như một artifact.

**Yêu cầu**: Project phải có `index.html` ở thư mục root.

**Script làm gì**:
- Cài đặt bundling dependency (parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline)
- Tạo config `.parcelrc` với hỗ trợ path alias
- Build với Parcel (không source map)
- Inline toàn bộ asset vào HTML duy nhất bằng html-inline

### Bước 4: Share Artifact với User

Cuối cùng, share file HTML đã bundle trong cuộc trò chuyện với user để họ có thể xem nó như một artifact.

### Bước 5: Test/Visualize Artifact (Tùy chọn)

Lưu ý: Đây là bước hoàn toàn tùy chọn. Chỉ thực hiện khi cần thiết hoặc được yêu cầu.

Để test/visualize artifact, dùng các tool có sẵn (bao gồm Skill khác hoặc tool built-in như Playwright hay Puppeteer). Thông thường, tránh test artifact trước (upfront) vì nó tăng latency giữa lúc request và lúc thấy được artifact hoàn thiện. Test sau, sau khi đã present artifact, nếu được yêu cầu hoặc nếu có vấn đề phát sinh.

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components
