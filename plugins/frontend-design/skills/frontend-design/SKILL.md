---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
allowed-tools: Read Grep Glob Bash Edit Write
argument-hint: <component-or-page>
---

# Frontend Design — Distinctive Interfaces

Create production-grade interfaces with high aesthetic quality, avoiding generic "AI slop".

## Design Thinking — Before coding

1. **Purpose**: What problem does this interface solve? Who uses it?
2. **Tone**: Choose one **aesthetic extreme** — brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian... Use these directions as inspiration, but design in a way that is authentic to the chosen aesthetic direction.
3. **Constraints**: Framework, performance, accessibility requirements.
4. **Differentiation**: What makes this interface **memorable**? 1 standout element.

**CRITICAL**: Choose a clear conceptual direction and execute it precisely. Bold maximalism or refined minimalism are both fine — what matters is intentionality.

Then implement working code that ensures:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Aesthetic Guidelines

### Typography
- Choose beautiful, distinctive fonts with personality — surprising choices with rich character that elevate the aesthetic. Pair a prominent display font with a subtle body font.
- **Avoid** generic fonts like Arial, Inter; choose distinctive fonts that elevate the aesthetic.

### Color & Theme
- Commit to a cohesive aesthetic. CSS variables for consistency.
- Dominant color with sharp accents — better than evenly distributed, bland palettes.

### Motion
- Use animation for effects and micro-interactions.
- CSS-only for plain HTML. Motion libraries for React when available.
- Focus on high-impact moments: staggered page load reveals (`animation-delay`), scroll-triggered animations, surprising hover states.
- 1 orchestrated page load > many scattered micro-interactions.

### Spatial Composition
- Asymmetry, overlap, diagonal flow, grid-breaking elements.
- Generous negative space OR controlled density — not the average of the two.

### Backgrounds & Visual Details
- Create atmosphere and depth instead of default solid colors. Add contextual effects and textures suited to the overall aesthetic.
- Gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, grain overlays.

## Anti-patterns — NEVER

- Overused font families (Inter, Roboto, Arial, system fonts)
- Purple gradients on white backgrounds
- Predictable layouts, cookie-cutter components
- Make creative interpretations and unexpected choices that feel designed for the specific context. Every design must be **distinct** — no two designs should look the same.
- Vary light/dark themes, fonts, aesthetics between projects. DO NOT converge on common choices (e.g.: Space Grotesk) across generations.

## Implementation

- **IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist → elaborate code with extensive animations and effects. Minimalist or refined → restraint, precision, meticulous attention to spacing, typography, and subtle details. Elegance comes from executing the vision correctly.
- Code must be production-grade, functional, and accessible.
- Write clean, well-documented code (comment WHY in English).

Claude is capable of creating extraordinary creative work. Do not hold back — show what can truly be created when thinking beyond conventions and fully committing to a distinctive design vision.
