# README structure

Generate the README from the real project (do not invent features). Place it in the repo root — GitHub surfaces a README in `.github`, the root, or `docs/`, and the root takes precedence over `docs/`.

## Required content

Cover GitHub's recommended elements ("About READMEs"): what the project does, why it is useful, how to get started, where to get help, who maintains and contributes.

## Header (centered)

Use the centered header from `../assets/README-header.md` (title + tagline + CI/license badges). GitHub's HTML sanitizer allows the `align` attribute on block elements (`div`, `p`, `h1`–`h6`) and `img`, so `<div align="center">` is the sanctioned way to center; CSS (`style="text-align:center"`) is stripped and will not work. Keep blank lines inside the `<div>` so the Markdown (heading, badges) renders.

## Numbered sections and subsections

Use an H1 title (inside the centered header), then numbered sections with numbered subsections:

```
## 1. Overview
## 2. Requirements
## 3. Installation
### 3.1 From source
### 3.2 From release
## 4. Usage
## 5. Configuration
## 6. Contributing
## 7. License
```

Numbering is a formal style chosen by preference; the typical GitHub README convention is unnumbered headings. GitHub auto-generates heading anchors either way, so numbering does not break navigation.

## Table of contents

For a long README, add a manual table of contents near the top (just below the header): a bulleted list of anchor links to each section. GitHub auto-generates an anchor from each heading by lowercasing it, replacing spaces with hyphens, and stripping punctuation — e.g. `## 3. Installation` becomes `#3-installation`:

```
## Table of Contents

- [1. Overview](#1-overview)
- [2. Requirements](#2-requirements)
- [3. Installation](#3-installation)
- [4. Usage](#4-usage)
```

For a short README, skip the manual TOC and rely on GitHub's auto-generated table of contents (the outline menu in the rendered view).
