#!/usr/bin/env node
/**
 * check-invariants-approved.mjs — GUARD GATE-A (FRAMEWORK §8 trở thành runnable).
 *
 * invariants.<domain>.md là DRAFT do agent seed; theo luật file, dòng còn `[ ]` (chưa human
 * duyệt) KHÔNG được dùng làm tiêu chí tầng 0. Script này ĐẾM `[ ]` và:
 *  - mặc định: report tỉ lệ đã duyệt + liệt kê ID chưa duyệt. Exit 0.
 *  - `--gate`: exit 1 nếu CÒN bất kỳ invariant `[ ]` → chặn T0 chạy với oracle chưa hợp lệ.
 *  - `--gate --id-prefix INV-STK`: chỉ gate nhóm prefix (gate theo module trước khi audit module đó).
 *
 * Phá lỗ hổng GATE-A-DRAFT-UNENFORCED: invariant DRAFT toàn `[ ]` nhưng không gì chặn T0 (số dòng đếm động từ file).
 *
 * Dùng: node verify-workflow/check-invariants-approved.mjs [--gate] [--id-prefix <P>] [--file <md>]
 */
import { readFileSync, existsSync } from 'node:fs';

const argv = process.argv.slice(2);
const fileArg = argv.includes('--file') ? argv[argv.indexOf('--file') + 1] : 'verify-workflow/invariants.ecommerce.md';
const prefix = argv.includes('--id-prefix') ? argv[argv.indexOf('--id-prefix') + 1] : null;
const gate = argv.includes('--gate');

if (!existsSync(fileArg)) { console.error(`✖ Không thấy ${fileArg}`); process.exit(2); }

const lines = readFileSync(fileArg, 'utf8').split('\n');
// dòng bảng invariant: `| INV-XXX-N | WHEN... | THEN... | nguồn | [ ] |`
const rows = [];
for (const line of lines) {
  const idM = line.match(/\|\s*(INV-[A-Z]+-\d+)\s*\|/);
  if (!idM) continue;
  const id = idM[1];
  if (prefix && !id.startsWith(prefix)) continue;
  const approved = /\[\s*[xX]\s*\]/.test(line) && !/\[\s*\]/.test(line);
  rows.push({ id, approved });
}

const total = rows.length;
const approved = rows.filter((r) => r.approved).length;
const unapproved = rows.filter((r) => !r.approved);

console.log(`\n=== GATE-A INVARIANTS (${fileArg}${prefix ? ` | prefix ${prefix}` : ''}) ===`);
console.log(`  Đã duyệt: ${approved}/${total}`);
if (unapproved.length) {
  console.log(`  CHƯA duyệt (${unapproved.length}): ${unapproved.map((r) => r.id).join(', ')}`);
}

if (gate) {
  if (total === 0) { console.error(`\n✖ GATE-A: không tìm thấy invariant nào${prefix ? ` với prefix ${prefix}` : ''}.`); process.exit(1); }
  if (unapproved.length > 0) {
    console.error(`\n✖ GATE-A FAIL: ${unapproved.length} invariant chưa human duyệt → T0 KHÔNG được dùng chúng làm tiêu chí. Đánh [x] sau khi xác nhận nghiệp vụ.`);
    process.exit(1);
  }
  console.log(`\n✔ GATE-A PASS: mọi invariant đã duyệt — T0 dùng được làm oracle.`);
}
