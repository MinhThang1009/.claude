#!/usr/bin/env node
/**
 * route-enumerator.mjs — Liệt kê + ĐẾM mọi (method, path) handler ở backend.
 *
 * Đây là DENOMINATOR thật cho coverage-ledger T1 (mẫu số "có bao nhiêu route cần phủ
 * trong use-case/sequence"). KHÁC `check:routes` (dead-route detector chỉ in suspect, exit 0).
 *
 * Giới hạn TRUNG THỰC (không overclaim): regex-based, đếm `router.<method>('<path>'...)`;
 * KHÔNG resolve full URL (bỏ qua basePath ở module.js), KHÔNG bắt route động/biến,
 * KHÔNG theo router.route() chaining (repo này không dùng). `router.use(...)` không tính
 * (là middleware mount, không phải endpoint). Con số là mẫu-số tham chiếu, đủ cho ledger.
 *
 * Config-driven: đọc glob `layer_globs.route_layer` từ PROJECT.yaml (KHÔNG hardcode đường dẫn).
 * Đổi project = đổi route_layer trong PROJECT.yaml. (Regex `router.<method>` vẫn theo Express/JS —
 * stack khác cần đổi ROUTER_VAR_RE/buildMethodRe hoặc dùng route_enumerator_cmd riêng của stack.)
 *
 * Dùng: node verify-workflow/route-enumerator.mjs [--json] [--project <PROJECT.yaml>]
 * Output: TOTAL + breakdown per module. Exit 0 (enumerator, không gate — gate là check-ledger).
 */
import { readFileSync, existsSync, globSync } from 'node:fs';
import { basename, dirname } from 'node:path';

const argv = process.argv.slice(2);
const PROJECT = argv.includes('--project') ? argv[argv.indexOf('--project') + 1] : 'verify-workflow/PROJECT.yaml';
const DEFAULT_ROUTE_GLOB = 'backend/src/modules/*/routes.js';

function readRouteGlob() {
  if (!existsSync(PROJECT)) return DEFAULT_ROUTE_GLOB;
  const yaml = readFileSync(PROJECT, 'utf8');
  let inLayer = false;
  for (const raw of yaml.split('\n')) {
    const line = raw.replace(/#.*$/, '');
    if (/^\w[\w]*:/.test(line)) inLayer = /^layer_globs:/.test(line);
    else if (inLayer) {
      const m = line.match(/^\s+route_layer:\s*"([^"]+)"/);
      if (m) return m[1];
    }
  }
  return DEFAULT_ROUTE_GLOB;
}

// Tìm biến router: `const x = express.Router()` / `= Router()`. Mặc định luôn có 'router'.
const ROUTER_VAR_RE = /(?:const|let|var)\s+(\w+)\s*=\s*(?:express\.)?Router\s*\(/g;

function buildMethodRe(routerVars) {
  const names = [...new Set(['router', ...routerVars])].map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  // (varname).(method)( '<path>'
  return new RegExp(`\\b(${names})\\.(get|post|put|patch|delete)\\s*\\(\\s*(['"\`])([^'"\`]+)\\3`, 'g');
}

function enumerateFile(file, moduleName) {
  const src = readFileSync(file, 'utf8');
  const routerVars = [];
  let rv;
  while ((rv = ROUTER_VAR_RE.exec(src)) !== null) routerVars.push(rv[1]);
  const methodRe = buildMethodRe(routerVars);
  const routes = [];
  let m;
  while ((m = methodRe.exec(src)) !== null) {
    const line = src.slice(0, m.index).split('\n').length;
    routes.push({ method: m[2].toUpperCase(), path: m[4], router: m[1], module: moduleName, file, line });
  }
  // raw = tổng lời gọi .method( trên BẤT KỲ router var (để phát hiện path không bắt được)
  const rawRe = buildMethodRe(routerVars);
  const rawSrc = src.replace(new RegExp(`\\b(${[...new Set(['router', ...routerVars])].join('|')})\\.(get|post|put|patch|delete)\\s*\\(`, 'g'), 'µHIT');
  const rawCount = (rawSrc.match(/µHIT/g) || []).length;
  void rawRe;
  return { routes, rawCount, routerVars };
}

function main() {
  const routeGlob = readRouteGlob();
  const files = globSync(routeGlob);
  if (files.length === 0) {
    console.error(`✖ route_layer glob "${routeGlob}" match 0 file — kiểm PROJECT.yaml layer_globs.route_layer + chạy từ repo root.`);
    process.exit(2);
  }
  const all = [];
  let totalRaw = 0;
  const perModule = {};
  for (const rf of files.sort()) {
    // module = thư mục chứa file routes (generic: basename(dirname(file)))
    const moduleName = basename(dirname(rf));
    const { routes, rawCount } = enumerateFile(rf, moduleName);
    all.push(...routes);
    totalRaw += rawCount;
    const cur = perModule[moduleName] || { matched: 0, raw: 0 };
    perModule[moduleName] = { matched: cur.matched + routes.length, raw: cur.raw + rawCount };
  }

  if (process.argv.includes('--json')) {
    console.log(JSON.stringify({ total: all.length, totalRaw, routeGlob, perModule, routes: all }, null, 2));
    return;
  }

  console.log(`\n=== ROUTE DENOMINATOR (${routeGlob}) ===\n`);
  for (const [mod, c] of Object.entries(perModule).sort()) {
    const flag = c.matched !== c.raw ? `  ⚠️ matched ${c.matched} ≠ raw ${c.raw} (kiểm path xuống dòng)` : '';
    console.log(`  ${String(c.matched).padStart(3)}  ${mod}${flag}`);
  }
  console.log(`\n  TOTAL routes (denominator) = ${all.length}`);
  if (all.length !== totalRaw) {
    console.log(`  ⚠️ Tổng raw 'router.<method>(' = ${totalRaw} ≠ matched ${all.length} — có path không bắt được bằng regex, kiểm thủ công.`);
  }
  console.log(`\n  (Mẫu số cho coverage-ledger T1. KHÔNG resolve basePath/route động — xem giới hạn trong header.)`);
}

main();
