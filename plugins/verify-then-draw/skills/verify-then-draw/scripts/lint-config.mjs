#!/usr/bin/env node
/**
 * lint-config.mjs — Tự kiểm PROJECT.yaml (FRAMEWORK §10.4 từ "residual risk" thành "có guard").
 *
 * Phá lỗ hổng G4-CONFIG-UNVERIFIED: trước đây header chỉ self-claim "đã verify". Script này assert:
 *  (1) mọi glob trong layer_globs match ≥1 file thực (glob sai → completeness mù mà vẫn báo đạt);
 *  (2) mọi "npm run X" trong *_cmd tồn tại trong backend/package.json scripts.
 *
 * Dùng: node verify-workflow/lint-config.mjs [--gate]   (--gate: exit 1 nếu có lỗi)
 */
import { readFileSync, existsSync, globSync } from 'node:fs';

const PROJECT = 'verify-workflow/PROJECT.yaml';
const PKG = 'backend/package.json';
const gate = process.argv.includes('--gate');

if (!existsSync(PROJECT)) { console.error(`✖ Không thấy ${PROJECT}`); process.exit(2); }
const yaml = readFileSync(PROJECT, 'utf8');
const lines = yaml.split('\n');

// 1) Thu thập glob trong block layer_globs
const globs = {};
let inLayer = false;
for (const raw of lines) {
  const line = raw.replace(/#.*$/, '');
  if (/^\w[\w]*:/.test(line)) inLayer = /^layer_globs:/.test(line);
  else if (inLayer) {
    const m = line.match(/^\s+(\w+):\s*"([^"]+)"/);
    if (m) globs[m[1]] = m[2];
  }
}

// 2) Thu thập "npm run X" kèm context: "cd frontend"→FE, "cd backend"→BE, else→ROOT
const FE_PKG = 'frontend/package.json';
const ROOT_PKG = 'package.json';
const npmScripts = [];
for (const raw of lines) {
  const m = raw.match(/(.*)npm run ([\w:-]+)/);
  if (!m) continue;
  const ctx = m[1];
  const where = /cd frontend|frontend\b/.test(ctx) ? 'FE' : /cd backend|backend\b/.test(ctx) ? 'BE' : 'ROOT';
  npmScripts.push({ name: m[2], where });
}
const loadScripts = (p) => (existsSync(p) ? Object.keys(JSON.parse(readFileSync(p, 'utf8')).scripts || {}) : null);
const pkgByWhere = { BE: loadScripts(PKG), FE: loadScripts(FE_PKG), ROOT: loadScripts(ROOT_PKG) };
const pkgPath = { BE: PKG, FE: FE_PKG, ROOT: ROOT_PKG };

const errors = [];
const ok = [];

console.log(`\n=== LINT PROJECT.yaml ===`);
console.log(`\n[1] layer_globs match file thực:`);
for (const [key, pat] of Object.entries(globs)) {
  // glob path nhiều file dùng dấu phẩy? PROJECT.yaml mỗi glob 1 pattern; hỗ trợ "a,b"
  const pats = pat.split(',').map((s) => s.trim());
  let hits = 0;
  for (const p of pats) { try { hits += globSync(p).length; } catch { /* glob lỗi */ } }
  if (hits > 0) { ok.push(`${key} → ${hits} file`); console.log(`  ✔ ${key.padEnd(15)} ${pat}  (${hits} file)`); }
  else { errors.push(`layer_globs.${key} "${pat}" match 0 file`); console.log(`  ✖ ${key.padEnd(15)} ${pat}  → 0 FILE`); }
}

console.log(`\n[2] npm scripts tồn tại (ROOT/BE/FE package.json):`);
const seen = new Set();
for (const { name, where } of npmScripts) {
  const key = where + ':' + name;
  if (seen.has(key)) continue;
  seen.add(key);
  const scripts = pkgByWhere[where];
  if (!scripts) { console.log(`  ⚠️ npm run ${name} (${where}) — không đọc được ${pkgPath[where]}`); continue; }
  if (scripts.includes(name)) console.log(`  ✔ [${where}] npm run ${name}`);
  else { errors.push(`[${where}] npm run ${name} không có trong ${pkgPath[where]}`); console.log(`  ✖ [${where}] npm run ${name}  → KHÔNG TỒN TẠI`); }
}

console.log(`\n  OK: ${ok.length} glob | Lỗi: ${errors.length}`);
if (errors.length) { console.log('  ' + errors.map((e) => '• ' + e).join('\n  ')); }

if (gate && errors.length) { console.error(`\n✖ LINT FAIL: config trỏ sai (${errors.length} lỗi).`); process.exit(1); }
if (gate) console.log(`\n✔ LINT PASS.`);
