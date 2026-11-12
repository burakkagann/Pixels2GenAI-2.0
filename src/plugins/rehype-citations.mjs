/**
 * rehype-citations (BLD-150, CIT-5a): turns every [n] in a lesson's prose into a
 * link to its entry in the References list, with no edit to the MDX files.
 *
 *  - The list is the first `.refs` element holding an <ol>; its <li>s get id="ref-n".
 *  - Each [n] / [n, m] / [n–m] in running text becomes <sup class="cite">[n][m]</sup>
 *    (CIT-2b). Every number is its own link: id="cite-n-k" (k = nth use of n).
 *  - Each entry gets back links: "↑" for one use, "↑ a b c" for several (CIT-3a).
 *  - Skipped: code, pre, math, links, the list itself. A group with any number
 *    outside 1..N stays plain text ([0, 1], [200, 200, 0]).
 *  - A page without References is left unchanged.
 *
 * Works on both hast elements and MDX JSX nodes, because the lessons write the
 * References as raw HTML, which MDX parses as JSX. Without the ~2 KB script
 * (src/components/lesson/Citations.astro) the jumps still work.
 */

const SKIP_TAGS = new Set(['code', 'pre', 'a', 'button', 'script', 'style', 'textarea', 'CodeBlock']);
const SKIP_CLASSES = ['katex', 'math-inline', 'math-display', 'refs', 'cite', 'cite-back'];
const MARKER = /\s?\[(\d+(?:\s*[,–-]\s*\d+)*)\]/g;

const isJsx = (n) => n.type === 'mdxJsxFlowElement' || n.type === 'mdxJsxTextElement';
const isEl = (n) => n.type === 'element' || isJsx(n);
const tagOf = (n) => (n.type === 'element' ? n.tagName : n.name);

function classesOf(n) {
  if (n.type === 'element') {
    const c = n.properties?.className;
    return Array.isArray(c) ? c : c ? String(c).split(/\s+/) : [];
  }
  if (isJsx(n)) {
    const a = n.attributes?.find((x) => x.name === 'class' || x.name === 'className');
    return typeof a?.value === 'string' ? a.value.split(/\s+/) : [];
  }
  return [];
}

function setId(n, id) {
  if (n.type === 'element') (n.properties ||= {}).id = id;
  else n.attributes.push({ type: 'mdxJsxAttribute', name: 'id', value: id });
}

function textOf(n, skipTag = true) {
  if (n.type === 'text') return n.value;
  if (!n.children) return '';
  if (skipTag && isEl(n) && classesOf(n).includes('tag')) return '';
  return n.children.map((c) => textOf(c, skipTag)).join('');
}

function findRefsList(node) {
  if (isEl(node) && classesOf(node).includes('refs')) {
    const ol = (function find(n) {
      for (const c of n.children || []) {
        if (isEl(c) && tagOf(c) === 'ol') return c;
        const d = isEl(c) && find(c);
        if (d) return d;
      }
      return null;
    })(node);
    if (ol) return ol;
  }
  for (const c of node.children || []) {
    const r = findRefsList(c);
    if (r) return r;
  }
  return null;
}

const el = (tagName, properties, children) => ({ type: 'element', tagName, properties, children });
const txt = (value) => ({ type: 'text', value });

// "Source 2: Galanter, P. (2003)": author and year, read from the entry.
function labelFor(entry) {
  const t = entry.replace(/\s+/g, ' ').trim();
  const m = t.match(/^(.*?\(\s*(?:\d{4}|n\.d\.)[^)]*\))/);
  return (m ? m[1] : t).slice(0, 70);
}

function parseNumbers(group) {
  const nums = [];
  for (const part of group.split(/\s*,\s*/)) {
    const r = part.split(/\s*[–-]\s*/).map(Number);
    if (r.length === 2 && r[1] >= r[0] && r[1] - r[0] < 50) for (let k = r[0]; k <= r[1]; k++) nums.push(k);
    else if (r.length === 1) nums.push(r[0]);
    else return [];
  }
  return nums;
}

export default function rehypeCitations() {
  return (tree, file) => {
    const ol = findRefsList(tree);
    if (!ol) return;
    const items = ol.children.filter((c) => isEl(c) && tagOf(c) === 'li');
    const N = items.length;
    if (!N) return;
    const labels = items.map((li) => labelFor(textOf(li)));
    items.forEach((li, i) => setId(li, `ref-${i + 1}`));

    const uses = {}; // ref number -> marker ids, in order
    const unmatched = new Set();

    const makeMarker = (num) => {
      uses[num] ||= [];
      const id = `cite-${num}-${uses[num].length + 1}`;
      uses[num].push(id);
      return el(
        'a',
        { className: ['cite-ref'], id, href: `#ref-${num}`, dataRef: String(num), ariaLabel: `Source ${num}: ${labels[num - 1]}` },
        [txt(`[${num}]`)],
      );
    };

    const convert = (text) => {
      MARKER.lastIndex = 0;
      const out = [];
      let last = 0;
      let m;
      while ((m = MARKER.exec(text))) {
        const nums = parseNumbers(m[1]);
        if (!nums.length || !nums.every((k) => k >= 1 && k <= N)) {
          unmatched.add(m[0].trim());
          continue;
        }
        if (m.index > last) out.push(txt(text.slice(last, m.index)));
        out.push(el('sup', { className: ['cite'] }, nums.map(makeMarker)));
        last = m.index + m[0].length;
      }
      if (!out.length) return null;
      if (last < text.length) out.push(txt(text.slice(last)));
      return out;
    };

    const visit = (node) => {
      if (!node.children) return;
      if (isEl(node)) {
        if (SKIP_TAGS.has(tagOf(node))) return;
        if (classesOf(node).some((c) => SKIP_CLASSES.includes(c))) return;
      }
      for (let i = 0; i < node.children.length; i++) {
        const c = node.children[i];
        if (c.type === 'text' && /\[\d/.test(c.value)) {
          const out = convert(c.value);
          if (out) {
            node.children.splice(i, 1, ...out);
            i += out.length - 1;
          }
        } else visit(c);
      }
    };
    visit(tree);

    // Back links, after the walk so every use is counted.
    items.forEach((li, i) => {
      const u = uses[i + 1];
      if (!u) return;
      const back = [];
      if (u.length === 1) {
        back.push(el('a', { href: `#${u[0]}`, ariaLabel: 'Back to the text' }, [txt('↑')]));
      } else {
        back.push(txt('↑ '));
        u.forEach((id, j) =>
          back.push(el('a', { href: `#${id}`, ariaLabel: `Back to use ${j + 1} of ${u.length}` }, [txt('abcdefghijklmnopqrstuvwxyz'[j] || String(j + 1))]), txt(' ')),
        );
      }
      li.children.push(txt(' '), el('span', { className: ['cite-back'] }, back));
    });

    if (unmatched.size && file) file.data.citationsUnmatched = [...unmatched];
  };
}
