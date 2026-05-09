// Commitlint config — Conventional Commits cho dotclaude.
// Override defaults vì tiếng Việt có dấu + thuật ngữ mixed.
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Header tối đa 100 ký tự (default 72 quá ngắn cho tiếng Việt có dấu).
    'header-max-length': [2, 'always', 100],
    // Cho phép body/footer dài hơn — cite Anthropic doc URLs hay dài.
    'body-max-line-length': [1, 'always', 200],
    'footer-max-line-length': [1, 'always', 200],
    // Subject case không enforce — tiếng Việt lowercase OK.
    'subject-case': [0],
    // Scope optional.
    'scope-empty': [0],
    // Types được phép — match commit history hiện có.
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'test',
        'chore',
        'ci',
        'build',
        'perf',
        'revert',
      ],
    ],
  },
};
