#!/usr/bin/env node
// Deterministic checks for a spec-pipeline feature folder.
// Usage: node validate-issues.js <feature-folder>   e.g. specs/S1-my-feature
// Exit codes: 0 = PASS, 1 = failures found, 2 = usage error.
'use strict';
const fs = require('fs');
const path = require('path');

const dir = process.argv[2];
if (!dir || !fs.existsSync(dir)) {
  console.error('Usage: node validate-issues.js <feature-folder>  e.g. specs/S1-my-feature');
  process.exit(2);
}
const issuesDir = path.join(dir, 'issues');
const errors = [];

function frontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return null;
  const out = {};
  for (const line of m[1].split(/\r?\n/)) {
    const i = line.indexOf(':');
    if (i > 0) out[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return out;
}
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();

if (!fs.existsSync(issuesDir)) {
  console.log('FAIL\n- no issues/ folder in ' + dir);
  process.exit(1);
}
const files = fs.readdirSync(issuesDir).filter((f) => /^S\d+-I\d+-.*\.md$/.test(f));
const issues = [];
for (const f of files) {
  const text = fs.readFileSync(path.join(issuesDir, f), 'utf8');
  const meta = frontmatter(text);
  if (!meta) { errors.push(`${f}: missing frontmatter`); continue; }
  const nameId = (f.match(/^(S\d+-I\d+)/) || [])[1];
  if (meta.id !== nameId) errors.push(`${f}: frontmatter id "${meta.id}" does not match filename id "${nameId}"`);
  issues.push({ f, id: meta.id || nameId, n: parseInt(nameId.split('-I')[1], 10), meta, text });
}
issues.sort((a, b) => a.n - b.n);

// 1. IDs sequential from I1 — append-only numbering, never reused
issues.forEach((it, i) => {
  if (it.n !== i + 1) errors.push(`numbering broken at ${it.id} (expected I${i + 1}): IDs must be sequential, never reused`);
});

// 2. Legal statuses; DONE needs evidence; deps exist and point backward; max one IN PROGRESS
const legal = /^(TODO|IN PROGRESS|DONE|BLOCKED: .+|DROPPED: .+)$/;
let inProgress = 0;
for (const it of issues) {
  const s = it.meta.status || '';
  if (!legal.test(s)) errors.push(`${it.id}: illegal status "${s}"`);
  if (s === 'IN PROGRESS') inProgress++;
  if (s === 'DONE' && (!it.meta.evidence || it.meta.evidence === 'none')) errors.push(`${it.id}: DONE without evidence`);
  const dep = (it.meta.depends_on || 'none').trim();
  if (dep !== 'none') {
    for (const d of dep.split(',').map((x) => x.trim())) {
      const target = issues.find((o) => o.id === d);
      if (!target) errors.push(`${it.id}: depends_on ${d} does not exist`);
      else if (target.n >= it.n) errors.push(`${it.id}: depends_on ${d} is not a lower-numbered issue`);
    }
  }
}
if (inProgress > 1) errors.push(`${inProgress} issues are IN PROGRESS — the maximum is 1`);

// 3. INDEX.md lists exactly the files on disk, both directions
const indexPath = path.join(issuesDir, 'INDEX.md');
if (!fs.existsSync(indexPath)) {
  errors.push('issues/INDEX.md is missing');
} else {
  const index = fs.readFileSync(indexPath, 'utf8');
  for (const it of issues) if (!index.includes(it.f)) errors.push(`INDEX.md does not list ${it.f}`);
  for (const m of index.matchAll(/S\d+-I\d+-[\w-]*\.md/g)) {
    if (!files.includes(m[0])) errors.push(`INDEX.md lists ${m[0]} which is not on disk`);
  }
}

// 4. Every SPEC section 11 criterion appears in some issue's Covers line
const specPath = path.join(dir, 'SPEC.md');
if (!fs.existsSync(specPath)) {
  errors.push('SPEC.md is missing');
} else {
  const spec = fs.readFileSync(specPath, 'utf8');
  const after = spec.split(/^## 11\..*$/m)[1];
  const s11 = after ? after.split(/^## /m)[0] : '';
  const criteria = [...s11.matchAll(/^- \[[ x]\] (.+)$/gm)].map((m) => m[1].split('— verified by')[0].trim());
  if (criteria.length === 0) errors.push('SPEC.md section 11 has no "- [ ]" acceptance criteria');
  const allCovers = norm(issues.map((it) => (it.text.match(/^Covers: (.+)$/m) || ['', ''])[1]).join(' | '));
  for (const c of criteria) {
    const needle = norm(c).slice(0, 60);
    if (needle && !allCovers.includes(needle)) errors.push(`criterion not covered by any issue: "${c.slice(0, 70)}"`);
  }
}

// Status summary and blocker report (printed on PASS and FAIL alike —
// blocked work is invisible unless something surfaces it)
const counts = {};
for (const it of issues) {
  const k = (it.meta.status || 'MISSING').split(':')[0].trim();
  counts[k] = (counts[k] || 0) + 1;
}
const summary = Object.entries(counts).map(([k, v]) => `${v} ${k}`).join(', ');
const blocked = issues.filter((it) => (it.meta.status || '').startsWith('BLOCKED'));

if (errors.length) {
  console.log('FAIL');
  for (const e of errors) console.log('- ' + e);
  for (const it of blocked) console.log(`BLOCKED ${it.id}: ${it.meta.status.replace(/^BLOCKED:\s*/, '')}`);
  process.exit(1);
}
console.log(`PASS - ${issues.length} issues (${summary}): numbering sequential, statuses legal, INDEX matches disk, all section 11 criteria covered`);
for (const it of blocked) console.log(`BLOCKED ${it.id}: ${it.meta.status.replace(/^BLOCKED:\s*/, '')} -> run the unblock skill`);
