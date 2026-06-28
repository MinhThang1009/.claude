# README structure

Generate the README from the real project (do not invent features). Place it in the repo root — GitHub surfaces a README from `.github`, the root, or `docs/`, in that order of precedence (`.github` > root > `docs/`). The root is the conventional choice.

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
- [4. Configuration](#4-configuration)
  - [4.1 General settings](#41-general-settings)
  - [4.2 Advanced options](#42-advanced-options)
```

When a section has numbered subsections (4.1, 4.2…), nest them under their parent as indented bullets so the TOC mirrors the document outline. The anchor for a numbered subsection follows the same rule — the period is stripped, so `### 4.1 General settings` becomes `#41-general-settings` (no dot between `4` and `1`).

For a short README, skip the manual TOC and rely on GitHub's auto-generated table of contents (the outline menu in the rendered view).

## Links and images

Use relative links to other files in the repo (e.g. `[Contributing](CONTRIBUTING.md)`, `docs/CONTRIBUTING.md`), not absolute `https://github.com/...` URLs — GitHub recommends relative links so they keep working in clones, forks, and on other hosts. The same applies to embedded images: reference repo files relatively (`docs/screenshot.png`). External resources (the project site, CI badge endpoints) stay absolute.
