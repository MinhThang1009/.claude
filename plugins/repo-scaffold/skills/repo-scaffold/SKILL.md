---
name: repo-scaffold
description: This skill should be used when the user asks to "scaffold a repo", "set up a repo to production standard", "create the standard repo files", "add community health files", "dựng repo chuẩn github", "tạo file chuẩn cho repo", or initializes a new repository that needs README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, LICENSE, CODEOWNERS, issue/PR templates, dependabot, .gitignore, and .gitattributes plus GitHub configuration (description, branch protection, labels).
version: 0.1.0
---

# Repo Scaffold

Set up a new repository to production GitHub standard: generate the community-health files with project-tailored content in correct GitHub format, then configure the GitHub side (description, topics, branch protection, labels).

Follow the user's conventions in `~/.claude/rules/git.md` and `security.md` if present (they may not exist when this plugin is installed elsewhere — fall back to standard git/security best practice). Generate documentation in the project's language: English by default, Vietnamese (with full diacritics) when the project's convention is Vietnamese.

## Core principles

- Never overwrite blindly. Survey existing files first; skip any that already exist, and ask before updating one.
- Confirm outward-facing actions (set description, push, branch protection, labels) before running them, unless the user already said to proceed.
- Never invent values. Detect or ask for license, contact email, and owner; never leave a `{{PLACEHOLDER}}` in generated output.
- Pull canonical text from APIs (LICENSE, .gitignore, Code of Conduct) instead of hand-writing it.

## Workflow

### 1. Survey

- Detect stack, name, and purpose from manifests (`package.json`, `composer.json`, `go.mod`, `version.php`, `pyproject.toml`) and any existing README.
- Run `gh repo view --json name,owner,description,defaultBranchRef,visibility,licenseInfo`. If this fails because the repo has no GitHub remote yet, create it first (`gh repo create`) or generate the files now and defer the GitHub-config step (5) until a remote exists.
- Topics: derive from the detected stack and keywords (language, framework, domain); confirm with the user before applying — do not invent them.
- List existing health files: `git ls-files | grep -iE '^(LICENSE|README|CONTRIBUTING|SECURITY|CODE_OF_CONDUCT|CODEOWNERS|\.gitignore|\.gitattributes)'` and `git ls-files .github`.
- Report which files exist (keep) versus which are missing (create).

### 2. Decide (ask only what cannot be detected)

- License SPDX key (`mit`, `apache-2.0`, `gpl-3.0`, ...): detect from source headers or `licenseInfo`, else ask.
- Contact email (SECURITY + Code of Conduct): detect from `git config user.email` or copyright headers; confirm.
- `.gitignore` template name (`Node`, `Python`, `Go`, `Composer`, ...).
- Documentation language. State all assumptions in one line before generating.

### 3. Generate files

Write each file to the repo, filling its placeholders. Sources differ by file (shown below): LICENSE and `.gitignore` come from the GitHub API, the Code of Conduct is fetched, the README is generated, CODEOWNERS is written inline, and the rest are copied from `assets/`.

CRITICAL (Windows/Git-Bash): pass `gh api` paths WITHOUT a leading slash, or the shell rewrites them to filesystem paths. Use `gh api licenses/<key>`, NOT `gh api /licenses/<key>`.

- LICENSE: `gh api licenses/<spdx-key> --jq '.body' > LICENSE`
- .gitignore: `gh api gitignore/templates/<Name> --jq '.source' > .gitignore` (append project-specific lines if needed)
- CODE_OF_CONDUCT.md: WebFetch `https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md`, then replace `[INSERT CONTACT METHOD]` with the contact email. CONTRIBUTING.md links this file, so if the fetch fails, retry or remove that link rather than ship a dead link.
- README.md: generate from the real project following `references/readme.md` — GitHub's recommended elements, a centered header (`assets/README-header.md`), numbered sections/subsections, CI/license badges, and a manual TOC for long READMEs. Do not invent features.
- .github/CODEOWNERS: write `* @{{OWNER}}` inline (one line, not an asset file).
- From `assets/` (fill `{{PROJECT_NAME}}`, `{{TAGLINE}}`, `{{OWNER}}`, `{{REPO}}`, `{{CONTACT_EMAIL}}`, `{{ECOSYSTEM}}`, `{{DATE}}`, `{{RELEASE_TYPE}}`):
  - Always: CONTRIBUTING.md, SECURITY.md, SUPPORT.md, CHANGELOG.md, .editorconfig, .gitattributes, .github/PULL_REQUEST_TEMPLATE.md, .github/ISSUE_TEMPLATE/{bug_report,feature_request}.md, .github/ISSUE_TEMPLATE/config.yml, .github/dependabot.yml.
  - Optional (offer based on project type): .github/FUNDING.yml (sponsorship), GOVERNANCE.md (community project), CITATION.cff (academic/citable).

Translate template prose to the project's language when it is not English; keep structure and headings.

### 4. Generate GitHub Actions workflows

Add a CI workflow tailored to the detected stack plus a release workflow. Follow the [workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions): top-level `name`, `on`, and `jobs`; each job sets `runs-on` and `steps`; each step uses `uses` or `run`.

- CI (`.github/workflows/ci.yml`): copy `assets/workflows/ci.yml` (a skeleton with a version matrix, a slot for caching, and the `ci-success` aggregate gate) and fill the stack-specific setup/install/lint/test — or start from GitHub's workflow template (`actions/starter-workflows`). Enable dependency caching via the `setup-*` action's `cache:` input (`setup-node` `cache: npm`, `setup-python` `cache: pip`) or `actions/cache`. Pin actions to their current major and verify each at its repo — the CI actions (`actions/checkout@v7`, `actions/setup-node@v6`, `actions/setup-python@v6`) AND the actions in every other workflow asset (release-please, dependency-review, dependabot-auto-merge, labeler, stale, commitlint). Prefer the latest LTS toolchain (`node-version: lts/*`), optionally testing `latest` in the matrix. Always create `ci.yml` — the README CI badge references it, and branch protection should require its single `ci-success` check (green only if every matrix job passed).
- Release (`.github/workflows/release.yml`): copy `assets/workflows/release.yml`. It triggers on a `v*` tag, builds an artifact, and creates the GitHub Release — or, if a release for that tag already exists (e.g. release-please published it), attaches the artifacts to it instead of failing. Customize the build step for the project.
- Dependency review (`.github/workflows/dependency-review.yml`): copy `assets/workflows/dependency-review.yml` — it flags PRs that introduce vulnerable dependencies.
- Auto-versioning (optional, pairs with Conventional Commits + CHANGELOG): copy `assets/workflows/release-please.yml`. On push to `main`, release-please opens a release PR that bumps the version and CHANGELOG; merging it creates the tag + Release, which triggers `release.yml` to build and attach artifacts. Fill `{{RELEASE_TYPE}}` with the stack's release-please type (the asset comment lists the supported values). The created tag triggers `release.yml` only if release-please uses a PAT secret (`RELEASE_PLEASE_TOKEN`), not the default `GITHUB_TOKEN`.
- Dependabot auto-merge (optional, zero-touch updates): copy `assets/workflows/dependabot-auto-merge.yml` — it auto-merges Dependabot PRs for patch/minor updates once CI passes (major updates stay manual). Requires branch protection ("Require status checks") and the repo's "Allow auto-merge" setting (`gh repo edit --enable-auto-merge`).
- Commitlint (recommended when using release-please): copy `assets/workflows/commitlint.yml` + `assets/commitlint.config.js` (to the repo root). It validates PR commit messages against Conventional Commits, so release-please's version bumps stay reliable.
- Stale bot (optional): copy `assets/workflows/stale.yml` — marks then closes inactive issues/PRs (exempts `pinned`/`security`).
- Labeler (optional): copy `assets/workflows/labeler.yml` and `assets/labeler.yml` → `.github/labeler.yml` — auto-labels PRs by changed paths.
- Release-notes config (optional): copy `assets/release-config.yml` → `.github/release.yml` — groups GitHub's auto-generated release notes by label.

### 5. Configure GitHub

Apply description, topics, branch protection (or ruleset, requiring the `ci-success` check), labels, security features (secret scanning + push protection, code-scanning default setup, Dependabot alerts, private vulnerability reporting), and merge settings (squash-only + auto-delete head branches). Confirm before applying. See `references/github-setup.md` for exact commands.

### 6. Commit

- New or empty repo: stage files, commit `chore: scaffold repo to production standard`, push to `main` (initial scaffolding).
- Existing repo with protected `main`: create a branch and open a PR (per `git.md`). Enable branch protection AFTER that PR merges, to avoid blocking the scaffold PR itself.

### 7. Verify

- `gh api repos/<owner>/<repo>/community/profile --jq '.health_percentage'` and report any missing files.
- `gh api repos/<owner>/<repo>/license --jq '.license.spdx_id'` to confirm GitHub detects the license.

## Resources

- `assets/` — file + workflow templates to copy and fill: community-health files, `README-header.md`, config files (`commitlint.config.js`, `labeler.yml`, `release-config.yml`), and `workflows/` (ci, release, release-please, dependency-review, dependabot-auto-merge, commitlint, stale, labeler).
- `references/readme.md` — README structure: required content, centered header, numbered sections, and table of contents.
- `references/github-setup.md` — exact gh commands for GitHub configuration and verification.
