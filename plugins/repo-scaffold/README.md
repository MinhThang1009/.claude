# repo-scaffold

A Claude Code plugin that scaffolds a new repository to production GitHub standard.

## What it does

Provides the `repo-scaffold` skill, which Claude activates when you ask to set up a new repository's standard files. It:

- Generates community-health files tailored to the project: README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, LICENSE, CODEOWNERS, issue/PR templates, dependabot, `.gitignore`, `.gitattributes`.
- Adds GitHub Actions workflows: a CI workflow tailored to the detected stack and a release-on-tag workflow.
- Configures the GitHub side: repository description, branch protection (or ruleset), and labels.

Content follows GitHub's community-standards format and is pulled from canonical sources where possible (LICENSE and `.gitignore` via the GitHub API, Code of Conduct from Contributor Covenant), with project-specific content generated from the repository itself.

## Requirements

- [`gh`](https://cli.github.com/) (GitHub CLI), authenticated (`gh auth status`) — used for every GitHub API call and configuration step.
- `git`.
- For the GitHub-configuration step, the repo needs a GitHub remote (run `gh repo create` first if it has none).

## Why it's useful

Every new repository needs the same production boilerplate in the correct GitHub format. This automates it intelligently: it reads the project to fill in real content instead of copying static templates.

## How to use

Install the plugin (see below), then, in any repository, ask Claude:

- "scaffold this repo"
- "set up the repo to production standard"
- "dựng repo chuẩn github" / "tạo file chuẩn cho repo"

The skill activates automatically and walks through: survey → decisions → file generation → workflows → GitHub configuration → commit → verification. It never overwrites existing files without asking and confirms outward-facing actions first.

## Install

Load it for a session:

```bash
claude --plugin-dir /path/to/repo-scaffold
```

For permanent use, add it to your plugin settings or publish it to a marketplace.

## Structure

```
repo-scaffold/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── LICENSE
└── skills/
    └── repo-scaffold/
        ├── SKILL.md
        ├── references/
        │   ├── readme.md          # README structure guidance
        │   └── github-setup.md    # exact gh configuration commands
        └── assets/                # community-health files + config files (commitlint, labeler, release-config)
            └── workflows/         # ci, release, release-please, dependency-review,
                                   # dependabot-auto-merge, commitlint, stale, labeler
```

SKILL.md → Resources lists every generated file.

## License

MIT. See [LICENSE](LICENSE).
