#!/usr/bin/env bash
# Test suite cho audit-logic-gate.py
# Chạy: bash plugins/audit-logic/hooks/test-audit-logic-gate.sh
# Windows: chạy qua Git Bash/MSYS — suite dựa vào MSYS tự chuyển path POSIX trong
# CLAUDE_PROJECT_DIR sang dạng Windows khi spawn python.exe native (không có python3).
# Bash thiếu cơ chế đó sẽ làm hook nhìn thấy path không tồn tại → kết quả sai.
HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/audit-logic-gate.sh"
STATE_DIR=$(mktemp -d)
mkdir -p "${STATE_DIR}/.claude"
STATE_FILE="${STATE_DIR}/.claude/audit-logic-state.json"
PASS=0; FAIL=0

run() {
  local label="$1" state_json="$2" event="${3:-Stop}" expect="$4"
  [ "$state_json" = "NONE" ] && rm -f "$STATE_FILE" || echo "$state_json" > "$STATE_FILE"
  local out code
  out=$(echo "{\"hook_event_name\": \"${event}\"}" | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
  code=$?
  local actual
  if [ $code -eq 2 ]; then actual="BLOCK"; elif [ $code -eq 0 ]; then actual="PASS"; else actual="ERROR"; fi
  if [ "$actual" = "$expect" ]; then
    PASS=$((PASS+1)); printf "  OK   [%-5s] %s\n" "$actual" "$label"
  else
    FAIL=$((FAIL+1)); printf "  MISS [%-5s] %s (expected %s)\n" "$actual" "$label" "$expect"
    echo "    out: $out"
  fi
}

echo "=== audit-logic-gate hook tests ==="

echo ""
echo "--- No state file (not running audit) ---"
run "no state file → PASS"                        "NONE"                                   "Stop"      "PASS"

echo ""
echo "--- All gates incomplete ---"
run "phase4=false, phase5=false → BLOCK"          '{"phase4_gate":false,"phase5_gate":false}' "Stop"  "BLOCK"

echo ""
echo "--- Phase 4 done only ---"
run "phase4=true, phase5=false → BLOCK"           '{"phase4_gate":true,"phase5_gate":false}'  "Stop"  "BLOCK"

echo ""
echo "--- Phase 5 done only ---"
run "phase4=false, phase5=true → BLOCK"           '{"phase4_gate":false,"phase5_gate":true}'  "Stop"  "BLOCK"

echo ""
echo "--- Phase 4+5 done, 6+7 missing ---"
run "phase4=true, phase5=true, 6/7 thiếu → BLOCK" '{"phase4_gate":true,"phase5_gate":true}'   "Stop"  "BLOCK"

echo ""
echo "--- All 4 gates complete ---"
run "cả 4 gates true → PASS"                      '{"findings_confirmed":true,"phase4_gate":true,"phase5_gate":true,"phase6_gate":true,"phase7_gate":true}' "Stop" "PASS"

echo ""
echo "--- Gates đã đóng hết → PASS kèm nhắc xóa state file ---"
echo '{"findings_confirmed":true,"phase4_gate":true,"phase5_gate":true,"phase6_gate":true,"phase7_gate":true}' > "$STATE_FILE"
out=$(echo '{"hook_event_name":"Stop"}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
code=$?
if [ $code -eq 0 ] && echo "$out" | grep -q "Xoa .claude/audit-logic-state.json"; then
  PASS=$((PASS+1)); printf "  OK   [PASS ] all-true → PASS + nhắc xóa state file (chống orphan đã đóng gate)\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [code=%d] expected PASS + nhắc xóa state file\n" "$code"
  echo "    out: $out"
fi

echo ""
echo "--- Hint không bao giờ gợi ý findings_confirmed: true ---"
echo '{"findings_confirmed":false,"phase4_gate":true,"phase5_gate":false}' > "$STATE_FILE"
out=$(echo '{"hook_event_name":"Stop"}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
if echo "$out" | grep -q 'set "phase5_gate": true' && ! echo "$out" | grep -q '"findings_confirmed": true'; then
  PASS=$((PASS+1)); printf "  OK   [BLOCK] hint single-field (phase5), không đụng findings_confirmed\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [BLOCK] hint sai format hoặc gợi ý findings_confirmed: true — implicit approval leak\n"
  echo "    out: $out"
fi

echo ""
echo "--- Warning khi đóng gates mà chưa confirm findings ---"
echo '{"findings_confirmed":false,"phase4_gate":true,"phase5_gate":true,"phase6_gate":true,"phase7_gate":true}' > "$STATE_FILE"
out=$(echo '{"hook_event_name":"Stop"}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
code=$?
if [ $code -eq 0 ] && echo "$out" | grep -q "WARNING"; then
  PASS=$((PASS+1)); printf "  OK   [PASS ] 4 gates true + findings_confirmed=false → PASS kèm WARNING\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [%s] expected PASS + WARNING (code=%d)\n" "$([ $code -eq 2 ] && echo BLOCK || echo PASS)" "$code"
  echo "    out: $out"
fi

echo ""
echo "--- stop_hook_active (stop lần 2 sau khi bị block) ---"
echo '{"phase4_gate":false,"phase5_gate":false}' > "$STATE_FILE"
out=$(echo '{"hook_event_name":"Stop","stop_hook_active":true}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
code=$?
if [ $code -eq 0 ]; then
  PASS=$((PASS+1)); printf "  OK   [PASS ] stop_hook_active=true + gates incomplete → PASS (cho phép dừng chờ user)\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [BLOCK] stop_hook_active=true → should PASS\n"
fi

echo ""
echo "--- SubagentStop always passes ---"
run "SubagentStop + gates incomplete → PASS"      '{"phase4_gate":false,"phase5_gate":false}' "SubagentStop" "PASS"

echo ""
echo "--- State file JSON hợp lệ nhưng không phải object (fail-safe) ---"
run "state = [1,2,3] → PASS (không crash)"        '[1,2,3]'                                   "Stop"  "PASS"
run "state = null → PASS (không crash)"           'null'                                      "Stop"  "PASS"

echo ""
echo "--- Hint chỉ show next gate (incremental) + có hướng dẫn orphan ---"
echo '{"findings_confirmed":false,"phase4_gate":false,"phase5_gate":false,"phase6_gate":false,"phase7_gate":false}' > "$STATE_FILE"
out=$(echo '{"hook_event_name":"Stop"}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
if echo "$out" | grep -q 'set "phase4_gate": true' && ! echo "$out" | grep -q 'set "phase5_gate"'; then
  PASS=$((PASS+1)); printf "  OK   [BLOCK] hint chỉ gợi ý gate kế tiếp (phase4)\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [BLOCK] hint không đúng dạng incremental single-field\n"
  echo "    out: $out"
fi
if echo "$out" | grep -q "mo coi"; then
  PASS=$((PASS+1)); printf "  OK   [BLOCK] message có recovery path cho orphaned state file\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [BLOCK] thiếu hướng dẫn xử lý orphaned state file\n"
  echo "    out: $out"
fi

echo ""
echo "--- Gate value kiểu string không được tính là đóng ---"
run "gates = \"true\" (string) → BLOCK"           '{"findings_confirmed":true,"phase4_gate":"true","phase5_gate":"true","phase6_gate":"true","phase7_gate":"true"}' "Stop" "BLOCK"

echo ""
echo "--- State file có UTF-8 BOM (PowerShell/notepad) vẫn phải block ---"
printf '\xef\xbb\xbf%s' '{"findings_confirmed":false,"phase4_gate":false,"phase5_gate":false,"phase6_gate":false,"phase7_gate":false}' > "$STATE_FILE"
out=$(echo '{"hook_event_name":"Stop"}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
code=$?
if [ $code -eq 2 ]; then
  PASS=$((PASS+1)); printf "  OK   [BLOCK] BOM + gates incomplete → BLOCK (utf-8-sig đọc được)\n"
else
  FAIL=$((FAIL+1)); printf "  MISS [code=%d] BOM làm gate âm thầm tắt — expected BLOCK\n" "$code"
  echo "    out: $out"
fi

echo ""
echo "--- State file UTF-16LE (PowerShell 5.1 redirect mặc định) → fail-open theo thiết kế ---"
if command -v iconv >/dev/null 2>&1; then
  printf '%s' '{"findings_confirmed":false,"phase4_gate":false,"phase5_gate":false,"phase6_gate":false,"phase7_gate":false}' | iconv -f UTF-8 -t UTF-16LE > "$STATE_FILE"
  out=$(echo '{"hook_event_name":"Stop"}' | CLAUDE_PROJECT_DIR="$STATE_DIR" bash "$HOOK" 2>&1)
  code=$?
  if [ $code -eq 0 ]; then
    PASS=$((PASS+1)); printf "  OK   [PASS ] UTF-16LE → fail-open PASS (gate tắt — hành vi fail-safe documented)\n"
  else
    FAIL=$((FAIL+1)); printf "  MISS [code=%d] UTF-16LE expected fail-open PASS\n" "$code"
    echo "    out: $out"
  fi
else
  printf "  SKIP iconv không có trên môi trường này — bỏ qua case UTF-16LE\n"
fi

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
