#!/usr/bin/env bash
# test-bash-commands.sh — test shell commands từ sub-agent-system skills/commands
# Chạy trên Linux/Mac/Windows Git Bash
# Exit code: 0 = all pass, 1 = failures

set -uo pipefail  # remove -e: không exit sớm khi test fail

PASS=0
FAIL=0
ERRORS=()

# Dùng PASS=$((PASS+1)) thay ((PASS++)) — tránh exit code 1 khi var=0 dưới set -e
ok()   { echo "  ✓ $1"; PASS=$((PASS+1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL+1)); ERRORS+=("$1"); }

# Setup mock environment
MOCK_HOME=$(mktemp -d)
MOCK_PROJECT=$(mktemp -d)
export HOME="$MOCK_HOME"

# Create mock .claude structure (simulate installed plugin)
mkdir -p "$MOCK_HOME/.claude/rules" "$MOCK_HOME/.claude/commands" "$MOCK_HOME/.claude/agents"
echo "# security rules" > "$MOCK_HOME/.claude/rules/security.md"
echo "# coding standards" > "$MOCK_HOME/.claude/rules/coding-standards.md"
echo "# CLAUDE.md" > "$MOCK_HOME/.claude/CLAUDE.md"

# Create mock project
mkdir -p "$MOCK_PROJECT/.claude/"{checkpoints,progress,alerts,tmp}
cd "$MOCK_PROJECT"
git init -q
git config user.email "test@test.com"
git config user.name "Test"
echo "test" > test.js && git add test.js && git commit -q -m "init"

echo "=== Convention-injector: \$HOME path resolution ==="
ls "$HOME/.claude/rules/"*.md > /dev/null 2>&1 && ok "\$HOME/.claude/rules/*.md glob works" || fail "\$HOME/.claude/rules/*.md glob failed"
cat "$HOME/.claude/rules/"*.md > /dev/null 2>&1 && ok "cat \$HOME/.claude/rules/*.md works" || fail "cat failed"
cat "$HOME/.claude/CLAUDE.md" > /dev/null 2>&1 && ok "cat \$HOME/.claude/CLAUDE.md works" || fail "CLAUDE.md read failed"

echo "=== Completion-checker: grep patterns ==="
echo "COMPLETION_CHECKLIST:" > /tmp/cc_test.txt
echo "[x] Task 1 done" >> /tmp/cc_test.txt
echo "[x] Task 2 done" >> /tmp/cc_test.txt
echo "[o] Task 3 skipped" >> /tmp/cc_test.txt

X_COUNT=$(grep -Fc '[x]' /tmp/cc_test.txt)
[ "$X_COUNT" = "2" ] && ok "grep -Fc '[x]' counts correctly ($X_COUNT)" || fail "grep [x] wrong count: $X_COUNT"

O_COUNT=$(grep -Fc '[o]' /tmp/cc_test.txt)
[ "$O_COUNT" = "1" ] && ok "grep -Fc '[o]' counts correctly ($O_COUNT)" || fail "grep [o] wrong count: $O_COUNT"

FLEX_COUNT=$(grep -Eic 'COMPLETION.{0,1}CHECKLIST' /tmp/cc_test.txt)
[ "$FLEX_COUNT" = "1" ] && ok "flex grep COMPLETION_CHECKLIST works" || fail "flex grep failed: $FLEX_COUNT"

# Test space variant
echo "COMPLETION CHECKLIST:" >> /tmp/cc_test2.txt
FLEX_COUNT2=$(grep -Eic 'COMPLETION.{0,1}CHECKLIST' /tmp/cc_test2.txt 2>/dev/null || echo 0)
[ "$FLEX_COUNT2" = "1" ] && ok "flex grep 'COMPLETION CHECKLIST' (space) also matches" || fail "space variant failed"

echo "=== Severity-gate: grep pattern ==="
cat > /tmp/findings.md << 'EOF'
| 🔴 CRITICAL | 2 |
**Severity:** 🔴 CRITICAL | **Agent:** T1
**Severity:** 🔴 CRITICAL | **Agent:** T2
EOF

# Correct pattern: exclude summary table line
RAW_COUNT=$(grep -c '🔴 CRITICAL' /tmp/findings.md)
# The bug: counts 3 (includes summary table)
FIXED_COUNT=$(grep '🔴 CRITICAL' /tmp/findings.md | grep -v '^|' | wc -l | tr -d ' ')
[ "$RAW_COUNT" = "3" ] && ok "Confirmed bug: raw grep counts summary table line ($RAW_COUNT instead of 2)" || fail "Expected 3 (including table), got $RAW_COUNT"
[ "$FIXED_COUNT" = "2" ] && ok "Fixed grep (exclude table lines) counts correctly ($FIXED_COUNT)" || fail "Fixed grep wrong: $FIXED_COUNT"

echo "=== Checkpoint-writer: git rev-parse ==="
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo NONE)
[ "$ROOT" != "NONE" ] && ok "git rev-parse --show-toplevel works: $ROOT" || fail "git rev-parse failed"

HEAD=$(git rev-parse HEAD 2>/dev/null || echo NONE)
[ "$HEAD" != "NONE" ] && ok "git rev-parse HEAD works: ${HEAD:0:8}..." || fail "git rev-parse HEAD failed"

echo "=== Pipeline-monitor: find pattern ==="
mkdir -p "$MOCK_PROJECT/.claude/progress"
echo "| ts | file | 10 | 2 | DONE |" > "$MOCK_PROJECT/.claude/progress/agent1-progress.md"
FOUND=$(find "$MOCK_PROJECT/.claude/progress" -name '*-progress.md' 2>/dev/null | wc -l | tr -d ' ')
[ "$FOUND" = "1" ] && ok "find progress files works ($FOUND file)" || fail "find progress failed: $FOUND"

echo "=== Install script: hook copy ==="
PLUGIN_DIR="$(dirname "$0")/../plugins/sub-agent-system"
[ -f "$PLUGIN_DIR/commands/plan-tasks.md" ] && ok "plan-tasks.md exists in plugin" || fail "plan-tasks.md missing"
[ -f "$PLUGIN_DIR/skills/completion-checker/SKILL.md" ] && ok "completion-checker SKILL.md exists" || fail "SKILL.md missing"
[ -f "$PLUGIN_DIR/hooks/post-commit" ] && ok "post-commit hook exists" || fail "post-commit hook missing"
[ -f "$PLUGIN_DIR/scripts/install.sh" ] && ok "install.sh exists" || fail "install.sh missing"

echo "=== install.sh dry run ==="
bash "$PLUGIN_DIR/scripts/install.sh" > /dev/null 2>&1 && ok "install.sh runs without error" || fail "install.sh failed"

# Cleanup
rm -rf "$MOCK_HOME" "$MOCK_PROJECT" /tmp/cc_test.txt /tmp/cc_test2.txt /tmp/findings.md

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
if [ ${#ERRORS[@]} -gt 0 ]; then
  echo "Failures:"
  for e in "${ERRORS[@]}"; do echo "  - $e"; done
fi

[ "$FAIL" = "0" ] && exit 0 || exit 1
