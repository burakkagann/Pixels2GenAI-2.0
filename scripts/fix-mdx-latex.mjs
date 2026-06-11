// One-off LaTeX brace escaper.
//
// Some untracked Module 04 lesson files contain inline LaTeX like
// `$D_{n-1}$` where the `{n-1}` is parsed by MDX as a JSX expression
// rather than a LaTeX subscript. This script reads each given file,
// finds inline math (`$...$`) and display math (`$$...$$`), and
// escapes `{` → `\{` and `}` → `\}` inside those regions only.

import { promises as fs } from 'node:fs';

const FILES = [
  'src/content/lessons/4.1.2.mdx',
  'src/content/lessons/4.1.3.mdx',
  'src/content/lessons/4.1.4.mdx',
  'src/content/lessons/4.1.5.mdx',
  'src/content/lessons/4.2.1.mdx',
  'src/content/lessons/4.2.2.mdx',
  'src/content/lessons/4.2.3.mdx',
  'src/content/lessons/4.2.4.mdx',
  'src/content/lessons/4.3.2.mdx',
  'src/content/lessons/4.3.3.mdx',
  'src/content/lessons/8.1.2.mdx',
  'src/content/lessons/8.1.3.mdx',
  'src/content/lessons/8.3.1.mdx',
];

// Escape `{` / `}` to `\{` / `\}` only when they are NOT already preceded
// by a backslash. Also collapse pre-existing `\\{` (over-escape from a
// previous run) back to `\{`.
function escapeBraces(inner) {
  // First collapse any over-escapes from a previous run: `\\{` → `\{`.
  let s = inner.replace(/\\\\\{/g, '\\{').replace(/\\\\\}/g, '\\}');
  // Then escape unescaped braces. Use a negative lookbehind to skip ones
  // that already have a single backslash before them.
  s = s.replace(/(?<!\\)\{/g, '\\{').replace(/(?<!\\)\}/g, '\\}');
  return s;
}

function escapeMath(content) {
  const lines = content.split('\n');
  let inFence = false;
  let inFrontmatter = false;
  let frontmatterDone = false;
  const out = [];

  for (let line of lines) {
    if (!frontmatterDone) {
      if (line === '---') {
        if (!inFrontmatter) inFrontmatter = true;
        else { inFrontmatter = false; frontmatterDone = true; }
        out.push(line);
        continue;
      }
      if (inFrontmatter) {
        out.push(line.replace(/\$([^$]*)\$/g, (m, inner) => `$${escapeBraces(inner)}$`));
        continue;
      }
    }

    if (/^```/.test(line.trim())) {
      inFence = !inFence;
      out.push(line);
      continue;
    }
    if (inFence) {
      out.push(line);
      continue;
    }

    line = line.replace(/\$\$([^$]+)\$\$/g, (m, inner) => `$$${escapeBraces(inner)}$$`);
    line = line.replace(/\$([^$\n]+?)\$/g, (m, inner) => `$${escapeBraces(inner)}$`);

    out.push(line);
  }
  return out.join('\n');
}

async function main() {
  for (const file of FILES) {
    try {
      const before = await fs.readFile(file, 'utf8');
      const after = escapeMath(before);
      if (before !== after) {
        await fs.writeFile(file, after);
        console.log(`updated ${file}`);
      } else {
        console.log(`no change ${file}`);
      }
    } catch (err) {
      console.error(`error on ${file}: ${err.message}`);
    }
  }
}

main();
