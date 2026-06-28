# GitHub Configuration Reference

Exact `gh` commands for step 5 (configure GitHub). Confirm each outward-facing action before running it.

NOTE (Windows/Git-Bash): `gh api` paths must NOT start with a leading slash, or the shell rewrites them to a filesystem path (`C:/Program Files/Git/...`). Use `gh api repos/OWNER/REPO/...`, never `gh api /repos/...`.

## Description and topics

```bash
gh repo edit OWNER/REPO --description "<one-line description>" \
  --add-topic <topic1> --add-topic <topic2>
```

A non-empty description is required for a 100% community profile. Topics aid discovery.

## Branch protection (classic)

Enable only when the user wants to enforce the PR flow. Require a PR, a passing CI check, up-to-date branches, and apply to admins too. A solo owner can still self-merge (0 required approvals).

```bash
gh api -X PUT repos/OWNER/REPO/branches/main/protection \
  -H "Accept: application/vnd.github+json" --input - <<'JSON'
{
  "required_status_checks": { "strict": true, "checks": [{ "context": "ci-success" }] },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null
}
JSON
```

`ci-success` is the aggregate gate job shipped in `assets/workflows/ci.yml` — green only if every `test` matrix job passed. Requiring this one check (instead of each matrix combo) means a PR that breaks any combo cannot merge, and the required-check list never goes stale when the matrix changes.

## Ruleset (modern alternative)

Rulesets are GitHub's newer mechanism: multiple can apply at once, are viewable with read access, and can restrict commit metadata. They coexist with classic branch protection (most restrictive wins). Configure them in the repo UI under Settings → Rules → Rulesets, or via `gh api repos/OWNER/REPO/rulesets`. Use classic branch protection for a quick solo setup; suggest rulesets when the user wants org-wide or layered rules.

## Labels

Create standard labels if missing:

```bash
gh label create "good first issue" --color 7057ff --description "Good for newcomers" --force
gh label create "help wanted"      --color 008672 --description "Extra attention is needed" --force
gh label create "question"         --color d876e3 --description "Further information is requested" --force
```

`bug`, `enhancement`, and `documentation` usually exist by default. Create `question` because SUPPORT.md and the issue-template chooser reference it.

## Dependabot

The `.github/dependabot.yml` file (from `assets/`) is enough; GitHub picks it up automatically once committed. No API call needed.

## Security features

GitHub recommends these (free for public repos; private repos may need GitHub Advanced Security). Enable per repository — not all are needed everywhere.

```bash
# Secret scanning + push protection (push protection requires secret scanning first)
gh repo edit OWNER/REPO --enable-secret-scanning --enable-secret-scanning-push-protection

# Code scanning (CodeQL) default setup — auto-detects languages, no workflow file needed
gh api -X PATCH repos/OWNER/REPO/code-scanning/default-setup -f state=configured

# Private vulnerability reporting — let people report vulnerabilities privately via the Security tab
gh api -X PUT repos/OWNER/REPO/private-vulnerability-reporting
```

- **Dependabot alerts + dependency graph**: on by default for public repos. For a private repo, enable with `gh api -X PUT repos/OWNER/REPO/vulnerability-alerts` and security updates with `gh api -X PUT repos/OWNER/REPO/automated-security-fixes`.
- **Dependency review**: add `assets/workflows/dependency-review.yml` — it blocks PRs that introduce vulnerable dependencies.

## Merge settings

Match the squash-default PR flow and keep branches tidy:

```bash
gh repo edit OWNER/REPO \
  --enable-squash-merge \
  --enable-merge-commit=false \
  --enable-rebase-merge=false \
  --delete-branch-on-merge \
  --enable-auto-merge
```

`--enable-auto-merge` is required for the Dependabot auto-merge workflow (`gh pr merge --auto`) to work.

## Verify

```bash
gh api repos/OWNER/REPO/community/profile --jq '.health_percentage'   # aim for 100
gh api repos/OWNER/REPO/license --jq '.license.spdx_id'               # confirms license detection
gh api repos/OWNER/REPO/branches/main/protection \
  --jq '{pr: (.required_pull_request_reviews != null), admins: .enforce_admins.enabled, checks: (.required_status_checks.checks | map(.context))}'
```
