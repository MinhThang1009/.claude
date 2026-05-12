---
name: frontend-design
description: Tạo giao diện frontend distinctive, production-grade, tránh AI slop aesthetics. Tự kích hoạt khi user yêu cầu build UI components, pages, hoặc web applications. Gọi /frontend-design hoặc khi user mô tả giao diện cần thiết kế.
allowed-tools: Read Grep Glob Bash Edit Write
argument-hint: "[mô tả component/page cần thiết kế]"
---

# Frontend Design — Distinctive Interfaces

Tạo giao diện production-grade với aesthetic cao, tránh generic "AI slop".

## Design Thinking — Trước khi code

1. **Purpose**: Giao diện giải quyết vấn đề gì? Ai dùng?
2. **Tone**: Chọn một **thái cực** thẩm mỹ — brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian... Dùng những hướng này làm cảm hứng, nhưng thiết kế sao cho trung thực với hướng thẩm mỹ đã chọn.
3. **Constraints**: Framework, performance, accessibility requirements.
4. **Differentiation**: Điều gì khiến giao diện này **đáng nhớ**? 1 yếu tố nổi bật.

**CRITICAL**: Chọn hướng conceptual rõ ràng và thực thi chính xác. Bold maximalism hay refined minimalism đều tốt — quan trọng là intentionality.

Sau đó implement working code đảm bảo:
- Production-grade và functional
- Visually striking và memorable
- Cohesive với clear aesthetic point-of-view
- Meticulously refined ở mọi chi tiết

## Aesthetic Guidelines

### Typography
- Chọn font đẹp, độc đáo, có cá tính — những lựa chọn bất ngờ, giàu character, nâng tầm aesthetic. Pair display font nổi bật với body font tinh tế.
- **Tránh** font generic như Arial, Inter; chọn font distinctive nâng tầm aesthetic.

### Color & Theme
- Cam kết với một aesthetic cohesive. CSS variables cho consistency.
- Dominant color với sharp accents — tốt hơn palettes phân bổ đều, nhạt nhẽo.

### Motion
- Dùng animation cho effects và micro-interactions.
- CSS-only cho HTML thuần. Motion library cho React khi available.
- Focus high-impact moments: staggered page load reveals (`animation-delay`), scroll-triggered animations, hover states bất ngờ.
- 1 orchestrated page load > nhiều micro-interactions rải rác.

### Spatial Composition
- Asymmetry, overlap, diagonal flow, grid-breaking elements.
- Generous negative space HOẶC controlled density — không trung bình.

### Backgrounds & Visual Details
- Tạo atmosphere và depth thay vì solid colors mặc định. Thêm contextual effects và textures phù hợp với overall aesthetic.
- Gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, grain overlays.

## Anti-patterns — KHÔNG BAO GIỜ

- Font families overused (Inter, Roboto, Arial, system fonts)
- Purple gradients on white backgrounds
- Predictable layouts, cookie-cutter components
- Diễn giải sáng tạo và đưa ra lựa chọn bất ngờ, cảm giác được thiết kế riêng cho context. Mỗi design phải **khác biệt** — không design nào giống nhau.
- Vary light/dark themes, fonts, aesthetics giữa các project. KHÔNG hội tụ về common choices (ví dụ: Space Grotesk) qua các lần generate.

## Implementation

- **IMPORTANT**: Match implementation complexity với aesthetic vision. Maximalist → elaborate code với extensive animations và effects. Minimalist hoặc refined → restraint, precision, chú ý tỉ mỉ spacing, typography và subtle details. Elegance đến từ việc thực thi vision đúng cách.
- Code phải production-grade, functional, accessible.
- Viết clean, well-documented code (comment WHY bằng tiếng Việt).

Claude có khả năng tạo creative work phi thường. Đừng giữ lại — hãy cho thấy điều thực sự có thể tạo ra khi tư duy vượt khuôn khổ và cam kết trọn vẹn với một tầm nhìn thiết kế riêng biệt.
