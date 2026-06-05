#!/usr/bin/env bash
# Test suite cho logic-audit-gate.py
# Chạy: bash ~/.claude/hooks/test-logic-audit-gate.sh
HOOK="$HOME/.claude/hooks/logic-audit-gate.sh"
STATE_DIR=$(mktemp -d)
mkdir -p "${STATE_DIR}/.claude"
STATE_FILE="${STATE_DIR}/.claude/logic-audit-state.json"
PASS=0; FAIL=0

run() {
  local label="$1" state_json="$2" event="${3:-Stop}" expect="$4"
  [ "$state_json" = "NONE" ] && rm -f "$STATE_FILE" || echo "$state_json" > "$STATE_FILE"
  local out code
  out=$(echo "{\"hook_event_name\": \"${event}\"}" | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
  code=$?
  local actual; [ $code -eq 2 ] && actual="BLOCK" || actual="PASS"
  if [ "$actual" = "$expect" ]; then
    PASS=$((PASS+1)); printf "  OK   [%-5s] %s\n" "$actual" "$label"
  else
    FAIL=$((FAIL+1)); printf "  MISS [%-5s] %s (expected %s)\n" "$actual" "$label" "$expect"
    echo "    out: $out"
  fi
}

echo "=== logic-audit-gate hook tests ==="

echo ""
echo "--- No state file (not running audit) ---"
run "no state file → PASS"                        "NONE"                                   "Stop"      "PASS"

echo ""
echo "--- Both gates incomplete ---"
run "phase4=false, phase5=false → BLOCK"          '{"phase4_gate":false,"phase5_gate":false}' "Stop"  "BLOCK"

echo ""
echo "--- Phase 4 done only ---"
run "phase4=true, phase5=false → BLOCK"           '{"phase4_gate":true,"phase5_gate":false}'  "Stop"  "BLOCK"

echo ""
echo "--- Phase 5 done only ---"
run "phase4=false, phase5=true → BLOCK"           '{"phase4_gate":false,"phase5_gate":true}'  "Stop"  "BLOCK"

echo ""
echo "--- Both gates complete ---"
run "phase4=true, phase5=true → PASS"             '{"phase4_gate":true,"phase5_gate":true}'   "Stop"  "PASS"

echo ""
echo "--- SubagentStop always passes ---"
run "SubagentStop + gates incomplete → PASS"      '{"phase4_gate":false,"phase5_gate":false}' "SubagentStop" "PASS"

echo ""
echo "--- Malformed state file ---"
echo "not-json" > "$STATE_FILE"
out=$(echo '{"hook_event_name":"Stop"}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
code=$?
if [ $code -eq 0 ]; then
  PASS=$((PASS+1)); printf "  OK   [PASS ] malformed JSON → fail-safe PASS\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [BLOCK] malformed JSON → should PASS\n"
fi

echo ""
echo "============================================"
printf "Total: %d, PASS: %d, FAIL: %d\n" "$((PASS+FAIL))" "$PASS" "$FAIL"
rm -rf "$STATE_DIR"
[ $FAIL -eq 0 ] && exit 0 || exit 1
