#!/usr/bin/env node
/**
 * mutation-survivors.mjs — Đóng gói bước "phân loại mutant SỐNG" của mutation-driven
 * test-strengthening loop (FRAMEWORK T0 §7). Thay việc parse mutation.json bằng tay.
 *
 * Đọc report JSON (Stryker mutation.json / format mutation-testing-elements schema),
 * liệt kê mọi mutant Survived theo file:line:col + mutator + replacement, và GỢI Ý phân loại:
 *   - EQUIVALENT-SUSPECT: boundary `>`->`>=` / `<`->`<=` (cap/so-sánh khi 2 vế bằng nhau cho
 *     cùng kết quả) — thường KHÔNG giết được bằng outcome; cần xác minh thủ công rồi mark
 *     `// Stryker disable next-line <Mutator>: <lý do>`.
 *   - LIKELY-KILLABLE: phần còn lại — viết test assert OUTCOME để giết.
 * Heuristic này chỉ là GỢI Ý (Equivalent Mutant Problem là undecidable) — luôn xác minh.
 *
 * Dùng: node verify-workflow/mutation-survivors.mjs [--report <path>] [--json]
 *   default report = backend/reports/mutation/mutation.json
 * Exit 0 (báo cáo). Dùng trong loop: chạy mutation_critical_cmd -> script này -> viết test -> lặp.
 */
import { readFileSync, existsSync } from 'node:fs';

const argv = process.argv.slice(2);
const report = argv.includes('--report') ? argv[argv.indexOf('--report') + 1] : 'backend/reports/mutation/mutation.json';
const asJson = argv.includes('--json');

if (!existsSync(report)) {
  console.error(`✖ Không thấy report "${report}". Chạy mutation_critical_cmd với reporter json trước (Stryker: --reporters json).`);
  process.exit(2);
}

// boundary-equivalent-suspect: replacement đổi `>`->`>=` hoặc `<`->`<=` (giữ chiều, thêm '=')
function isEquivalentSuspect(m) {
  if (m.mutatorName !== 'EqualityOperator') return false;
  const r = m.replacement || '';
  return /[^<>=]>=[^=]/.test(` ${r} `) || /[^<>=]<=[^=]/.test(` ${r} `) || r.includes('>=') || r.includes('<=');
}

const data = JSON.parse(readFileSync(report, 'utf8'));
const out = [];
let total = 0, killed = 0, survived = 0;
for (const [file, f] of Object.entries(data.files || {})) {
  for (const m of f.mutants) {
    total++;
    if (m.status === 'Killed' || m.status === 'Timeout') killed++;
    if (m.status !== 'Survived') continue;
    survived++;
    const loc = m.location.start;
    out.push({
      file, line: loc.line, col: loc.column,
      mutator: m.mutatorName,
      replacement: (m.replacement || '').replace(/\s+/g, ' ').slice(0, 70),
      classify: isEquivalentSuspect(m) ? 'EQUIVALENT-SUSPECT' : 'LIKELY-KILLABLE',
    });
  }
}
const score = total ? (killed * 100) / (killed + survived) : 0;
const killable = out.filter((x) => x.classify === 'LIKELY-KILLABLE');
const equiv = out.filter((x) => x.classify === 'EQUIVALENT-SUSPECT');

if (asJson) {
  console.log(JSON.stringify({ total, killed, survived, score: +score.toFixed(2), killable, equivalentSuspect: equiv }, null, 2));
  process.exit(0);
}

console.log(`\n=== MUTATION SURVIVORS (${report}) ===`);
console.log(`  total=${total} killed=${killed} survived=${survived} score=${score.toFixed(2)}%`);
console.log(`  → LIKELY-KILLABLE=${killable.length} (viết test giết) | EQUIVALENT-SUSPECT=${equiv.length} (xác minh → mark disable)\n`);
const fmt = (x) => `  ${x.classify === 'LIKELY-KILLABLE' ? '🎯' : '≈ '} L${x.line}:${x.col} ${x.mutator.padEnd(20)} → ${x.replacement}`;
if (killable.length) { console.log('LIKELY-KILLABLE (ưu tiên viết test assert OUTCOME):'); killable.forEach((x) => console.log(fmt(x))); }
if (equiv.length) { console.log('\nEQUIVALENT-SUSPECT (xác minh thủ công; nếu đúng equivalent → // Stryker disable next-line):'); equiv.forEach((x) => console.log(fmt(x))); }
console.log(`\n  Loop: giết killable → re-run mutation → tới khi chỉ còn equivalent (score chạm trần) hoặc ≥ break threshold.`);
