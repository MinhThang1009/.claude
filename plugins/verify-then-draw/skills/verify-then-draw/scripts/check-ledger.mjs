#!/usr/bin/env node
/**
 * check-ledger.mjs — Coverage-ledger ENFORCE (FRAMEWORK §5/§6 trở thành runnable).
 *
 * Đọc diagram-manifest.yaml + PROJECT.yaml(logic_heavy) + route-enumerator (denominator thật).
 * - Mặc định (report): in bảng status per type/module + denominator route vs số sơ đồ. Exit 0.
 * - `--gate`: ENFORCE — exit 1 nếu BẤT KỲ sơ đồ thuộc module logic_heavy CHƯA `signed`
 *   (chưa qua GATE-D human). Dùng ở CI/pre-push để "gate cứng" không còn là honor-system.
 *
 * TRUNG THỰC: KHÔNG tự map sơ đồ→route (không có link chính thức trong manifest) → chỉ in
 * 2 con số (route denominator vs #diagram) cho human so. Coverage gate dựa STATUS manifest,
 * là tín hiệu khách quan đo được (khác claim "% route phủ" giả của denominator cũ).
 *
 * Dùng: node verify-workflow/check-ledger.mjs [--gate]
 */
import { readFileSync, existsSync, statSync } from 'node:fs';
import { execSync } from 'node:child_process';

const MANIFEST = 'verify-workflow/diagram-manifest.yaml';
const PROJECT = 'verify-workflow/PROJECT.yaml';
const OUTPUT_ROOT = 'diagrams';
const STATUSES = ['pending', 'drawn', 'verified', 'signed'];
const SRC_EXT = { plantuml: 'puml', mermaid: 'mmd', dbml: 'dbml', drawio: 'drawio', latex: 'tex' };

// Phát hiện sơ đồ STALE: đã 'drawn'+ nhưng PNG thiếu HOẶC source mới hơn PNG (chưa re-render).
// Phá silent-failure: GATE-D có thể ký nhầm PNG cũ. Derive path theo naming {type}-{seq:02d}-{scope}.
function checkStaleness(entries) {
  const issues = [];
  for (const e of entries) {
    if (e.status === 'pending' || !e.seq) continue;
    const base = `${OUTPUT_ROOT}/${e.type}/${e.type}-${String(e.seq).padStart(2, '0')}-${e.scope}`;
    const src = `${base}.${SRC_EXT[e.tool] || 'puml'}`;
    const png = `${base}.png`;
    if (!existsSync(png)) { issues.push({ e, kind: 'PNG-MISSING', detail: png }); continue; }
    if (existsSync(src) && statSync(src).mtimeMs > statSync(png).mtimeMs) {
      issues.push({ e, kind: 'STALE', detail: `${src} mới hơn ${png} → cần re-render` });
    }
  }
  return issues;
}

function parseLogicHeavy(yaml) {
  const m = yaml.match(/logic_heavy:\s*\[([^\]]*)\]/);
  if (!m) return [];
  return m[1].split(',').map((s) => s.trim()).filter(Boolean);
}

function parseManifest(yaml) {
  const lines = yaml.split('\n');
  const entries = [];
  let currentType = null;
  for (const raw of lines) {
    const line = raw.replace(/#.*$/, '');
    const typeM = line.match(/^([a-z_]+):\s*$/);
    if (typeM) { currentType = typeM[1]; continue; }
    if (!/^\s*-\s*\{/.test(line)) continue;
    const status = (line.match(/status:\s*([\w-]+)/) || [])[1] || 'unknown';
    const module = (line.match(/module:\s*("?)([^,}"]+)\1/) || [])[2]?.trim() || '?';
    const scope = (line.match(/scope:\s*([^,}]+)/) || [])[1]?.trim() || '?';
    const seq = (line.match(/seq:\s*(\d+)/) || [])[1];
    const tool = (line.match(/tool:\s*([\w-]+)/) || [])[1] || 'plantuml';
    if (['usecase', 'component', 'state', 'sequence', 'erd', 'deployment', 'pipeline'].includes(currentType)) {
      entries.push({ type: currentType, scope, module, status, seq, tool });
    }
  }
  return entries;
}

function isLogicHeavy(moduleField, logicHeavy) {
  // module có thể là "orders" hoặc "orders+cart+payment"
  return moduleField.split('+').some((m) => logicHeavy.includes(m.trim()));
}

function main() {
  for (const f of [MANIFEST, PROJECT]) {
    if (!existsSync(f)) { console.error(`✖ Không thấy ${f} — chạy từ repo root.`); process.exit(2); }
  }
  const logicHeavy = parseLogicHeavy(readFileSync(PROJECT, 'utf8'));
  const entries = parseManifest(readFileSync(MANIFEST, 'utf8'));

  const byStatus = Object.fromEntries(STATUSES.map((s) => [s, 0]));
  for (const e of entries) byStatus[e.status] = (byStatus[e.status] || 0) + 1;

  console.log(`\n=== DIAGRAM LEDGER (${entries.length} sơ đồ) ===`);
  console.log('  status: ' + STATUSES.map((s) => `${s}=${byStatus[s] || 0}`).join('  '));

  const unsignedLH = entries.filter((e) => isLogicHeavy(e.module, logicHeavy) && e.status !== 'signed');
  console.log(`\n  logic_heavy = [${logicHeavy.join(', ')}]`);
  console.log(`  Sơ đồ logic_heavy CHƯA signed (GATE-D): ${unsignedLH.length}`);
  for (const e of unsignedLH) console.log(`    [${e.status.padEnd(8)}] ${e.type}-* ${e.scope} (${e.module})`);

  // Staleness: sơ đồ đã drawn+ nhưng PNG thiếu / source mới hơn PNG (chưa re-render)
  const stale = checkStaleness(entries);
  console.log(`\n  Sơ đồ STALE / thiếu PNG: ${stale.length}`);
  for (const s of stale) console.log(`    [${s.kind}] ${s.e.type}-${String(s.e.seq).padStart(2, '0')}-${s.e.scope}: ${s.detail}`);

  // Denominator route (tham chiếu, KHÔNG auto-map)
  try {
    const out = execSync('node verify-workflow/route-enumerator.mjs --json', { encoding: 'utf8' });
    const total = JSON.parse(out).total;
    const ucSeq = entries.filter((e) => ['usecase', 'sequence'].includes(e.type)).length;
    console.log(`\n  Tham chiếu (human so, KHÔNG auto-map): route denominator = ${total} | #use-case+sequence = ${ucSeq}`);
  } catch (e) {
    console.log(`\n  ⚠️ Không lấy được route denominator: ${e.message.split('\n')[0]}`);
  }

  if (process.argv.includes('--gate')) {
    if (stale.length > 0) {
      console.error(`\n✖ GATE FAIL: ${stale.length} sơ đồ STALE/thiếu PNG — re-render trước khi GATE-D (tránh ký nhầm bản cũ).`);
      process.exit(1);
    }
    if (unsignedLH.length > 0) {
      console.error(`\n✖ GATE FAIL: ${unsignedLH.length} sơ đồ logic_heavy chưa qua GATE-D (signed). Không được tuyên bố "done".`);
      process.exit(1);
    }
    console.log(`\n✔ GATE PASS: mọi sơ đồ logic_heavy đã signed + không stale.`);
  }
}

main();
