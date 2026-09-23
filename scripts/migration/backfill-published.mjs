#!/usr/bin/env node
/**
 * One-shot: backfill `published: YYYY-MM-DD` into every lesson's frontmatter
 * from the date the lesson first went live, derived from git history.
 * Read-only on v1 (git log / cat-file only). Priority per lesson:
 *
 *   1. deploy  : earliest v1 commit whose subject deploys/adds the lesson id
 *                ("Deploy Module 12.7.1 - ...", "Add Modules 1.3.1, 2.1.1-2.1.4").
 *                Subjects that only Update / Finalize a lesson don't count.
 *   2. v1      : first v1 commit since the 2025-10-01 module scaffold in which a
 *                README.rst anywhere under the lesson's folder is real content
 *                (> 5 KB; scaffold stubs are ~150-300 B). Folder-level, so the
 *                2026-02-06 "Flatten Module NN" moves out of nested subfolders
 *                don't hide earlier history.
 *   3. v2      : the lesson never got content in v1 (its README is still a stub):
 *                first v2 commit, after the 2026-05-25 bulk-migration revert, in
 *                which the MDX is real content (> 5 KB).
 *
 * Lessons that already have `published:` are left alone.
 *   node scripts/migration/backfill-published.mjs "<path to v1 repo>" [--write]
 */
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const V1 = process.argv[2];
const WRITE = process.argv.includes('--write');
if (!V1 || !fs.existsSync(path.join(V1, '.git'))) {
  console.error('Usage: node scripts/migration/backfill-published.mjs "<path to v1 repo>" [--write]');
  process.exit(1);
}
const git = (repo, ...args) => execFileSync('git', ['-C', repo, ...args], { encoding: 'utf8', maxBuffer: 64 << 20 });
const V2 = process.cwd();

// 1. v1 deploy/add subjects ("moddule" typo included).
const deploy = new Map();
for (const line of git(V1, 'log', '--reverse', '--format=%as\t%s').trim().split('\n')) {
  const [date, subject] = line.split('\t');
  if (!/\b(deploy|add)\b/i.test(subject) || !/mod+ules?\b/i.test(subject)) continue;
  const deployPart = subject.split(/\b(update|updated|finali[sz]ed)\b/i)[0];
  const ids = new Set();
  for (const m of deployPart.matchAll(/\b(\d+)\.(\d+)\.(\d+)\s*[-–]\s*\1\.\2\.(\d+)\b/g))
    for (let k = Number(m[3]); k <= Number(m[4]); k++) ids.add(`${m[1]}.${m[2]}.${k}`);
  for (const m of deployPart.matchAll(/\b\d+\.\d+\.\d+\b/g)) ids.add(m[0]);
  for (const id of ids) if (!deploy.has(id)) deploy.set(id, date);
}

// 2 + 3. First commit where a matching file under `pathspec` exceeds 5 KB.
function firstSubstantial(repo, since, pathspec, fileRe, follow = false) {
  // Newest-first, reversed here: git's --follow does not track renames
  // correctly when combined with --reverse.
  const args = ['log', `--since=${since}`, '--format=@%h %as', '--name-only'];
  if (follow) args.push('--follow');
  const out = git(repo, ...args, '--', pathspec);
  const commits = [];
  for (const line of out.split('\n')) {
    if (line.startsWith('@')) { const [hash, date] = line.slice(1).split(' '); commits.push({ hash, date, files: [] }); continue; }
    if (fileRe.test(line)) commits.at(-1)?.files.push(line);
  }
  for (const { hash, date, files } of commits.reverse()) {
    for (const f of files) {
      try { if (Number(git(repo, 'cat-file', '-s', `${hash}:${f}`).trim()) > 5000) return date; } catch { /* deleted here */ }
    }
  }
  return null;
}

const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) =>
  e.isDirectory() ? walk(path.join(d, e.name)) : e.name.endsWith('.mdx') ? [path.join(d, e.name)] : []);

const tally = { deploy: 0, v1: 0, v2: 0, kept: 0, none: 0 };
for (const file of walk(path.join(V2, 'src/content/lessons'))) {
  const id = path.basename(file).split('_')[0];
  let src = fs.readFileSync(file, 'utf8');
  if (/^published:/m.test(src.slice(0, src.indexOf('\n---', 4)))) { tally.kept++; continue; }
  const rel = path.relative(path.join(V2, 'src/content/lessons'), file).replace(/\\/g, '/');
  let date = deploy.get(id), source = 'deploy';
  if (!date) { date = firstSubstantial(V1, '2025-09-30', `content/${rel.replace(/\.mdx$/, '')}`, /README\.rst$/); source = 'v1'; }
  if (!date) { date = firstSubstantial(V2, '2026-05-25', `src/content/lessons/${rel}`, /\.mdx$/, true); source = 'v2'; }
  if (!date) { tally.none++; console.log(`${id.padEnd(7)} ??????????  no date found`); continue; }
  tally[source]++;
  console.log(`${id.padEnd(7)} ${date}  ${source}`);
  if (WRITE) {
    const nl = src.includes('\r\n') ? '\r\n' : '\n';
    src = src.replace(/^(duration:.*)$/m, `$1${nl}published: ${date}`);
    fs.writeFileSync(file, src);
  }
}
console.log(tally, WRITE ? '(written)' : '(dry run: pass --write to apply)');
