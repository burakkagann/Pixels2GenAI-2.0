/**
 * The concept framework rules (FW-1 to FW-6, check rules FW-5; picks TT-A + 3 conditions, 16 Nov 2026).
 * One source for both places that enforce them:
 *   - scripts/check-concepts.mjs (npm run check, before every build), on every concept file and every lesson;
 *   - the components (ConceptScreen, Recall), which throw on the same faults at build time, as Diagram does.
 * Plain functions that return a list of error strings; file checks go through an `exists(path)` function so the
 * node tests (tests/concepts/) can run every rule on in-memory fixtures.
 *
 * Concept file: src/content/concepts/<id>.mdx, frontmatter as in src/content/config.ts, body = the Explain text.
 * Lesson: the MDX of a lesson that uses <ConceptScreen>; its screens are read from the tags in source order.
 */

export const MAX_EXPLAIN_WORDS = 70;
export const MAX_FEEDBACK_WORDS = 25;
/** The key idea (CR-2, 16 Nov 2026): one sentence for the step's Concept row, Earlier links and Wrap up. */
export const MAX_KEY_IDEA_WORDS = 20;
export const MAX_CONCEPT_SCREENS = 4;
export const THEMES = ['light', 'dark'];

/** Words in a Markdown body: code spans count as words, markup does not. */
export function wordCount(text) {
  const plain = String(text ?? '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[`*_#>[\]()]/g, ' ')
    .trim();
  return plain ? plain.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length : 0;
}

/** Sentences end in . ! or ? followed by a space or the end ("(90 + 30 + 0) / 3 = 40." is one). */
export function sentenceCount(text) {
  return (String(text ?? '').trim().match(/[.!?](?=\s|$)/g) ?? []).length || 1;
}

/** Where a figure folder lives on disk: /workshop-media/... at the repo root, anything else under public/. */
export function folderOnDisk(folder) {
  return folder.startsWith('/workshop-media/') ? folder.slice(1) : `public${folder}`;
}

/** The files a concept figure needs: light, dark and phone, per theme. */
export function figureFiles(figure) {
  const ext = figure.ext ?? 'webp';
  const base = `${folderOnDisk(figure.folder)}/${figure.name}`;
  return THEMES.flatMap((theme) => [`${base}.${theme}.${ext}`, `${base}.${theme}.phone.${ext}`]);
}

function questionErrors(where, question) {
  const errors = [];
  if (!question || typeof question !== 'object') return [`${where}: missing`];
  if (!question.q || !String(question.q).trim()) errors.push(`${where}: no question text`);
  const options = Array.isArray(question.options) ? question.options : [];
  if (options.length < 2 || options.length > 4) errors.push(`${where}: needs 2-4 options, has ${options.length}`);
  const correct = options.filter((o) => o?.correct === true).length;
  if (correct !== 1) errors.push(`${where}: needs exactly one correct option, has ${correct}`);
  options.forEach((option, i) => {
    const label = `${where} option ${i + 1} ("${option?.text ?? ''}")`;
    if (!option?.text) errors.push(`${label}: no text`);
    if (!option?.why || !String(option.why).trim()) {
      errors.push(`${label}: no feedback (FW-4: one sentence per option)`);
      return;
    }
    if (sentenceCount(option.why) > 1) errors.push(`${label}: feedback is more than one sentence`);
    if (wordCount(option.why) > MAX_FEEDBACK_WORDS) errors.push(`${label}: feedback over ${MAX_FEEDBACK_WORDS} words`);
  });
  return errors;
}

/** Splits "Gonzalez & Woods, 2018" or "Harris et al., 2020" into surnames and year; null if not that form. */
export function parseCite(cite) {
  const match = String(cite).match(/^(.+?),\s*(\d{4}[a-z]?)$/);
  if (!match) return null;
  const names = match[1].replace(/\bet al\.?/, '').split(/\s*(?:&|,|\band\b)\s*/).map((n) => n.trim()).filter(Boolean);
  return names.length ? { names, year: match[2] } : null;
}

/**
 * Rules on one concept file.
 * @param {{ id: string, data: any, body: string }} concept
 * @param {(path: string) => boolean} exists  path relative to the repo root
 */
export function conceptErrors(concept, exists) {
  const { id, data = {}, body = '' } = concept;
  const where = `concept "${id}"`;
  const errors = [];
  if (data.id !== undefined && data.id !== id) errors.push(`${where}: frontmatter id "${data.id}" is not the file name`);
  if (!data.title) errors.push(`${where}: no title`);
  // CR-2: one sentence, at most 20 words, reused in the step's Concept row, the Earlier link and the Wrap up list.
  if (!data.keyIdea || !String(data.keyIdea).trim()) errors.push(`${where}: no keyIdea (one sentence, at most ${MAX_KEY_IDEA_WORDS} words; CR-2)`);
  else {
    if (sentenceCount(data.keyIdea) > 1) errors.push(`${where}: keyIdea is more than one sentence (CR-2)`);
    const keyWords = wordCount(data.keyIdea);
    if (keyWords > MAX_KEY_IDEA_WORDS) errors.push(`${where}: keyIdea is ${keyWords} words, over ${MAX_KEY_IDEA_WORDS} (CR-2)`);
  }

  const figure = data.figure;
  if (!figure || !figure.name || !figure.folder) {
    errors.push(`${where}: no figure`);
  } else {
    if (!/^\/[\w/-]+$/.test(figure.folder)) errors.push(`${where}: figure folder must be a plain path: ${figure.folder}`);
    if (!/^[\w-]+$/.test(figure.name)) errors.push(`${where}: figure name must be a plain name: ${figure.name}`);
    for (const file of figureFiles(figure)) if (!exists(file)) errors.push(`${where}: missing figure file ${file}`);
    if (!figure.alt || String(figure.alt).trim().length < 10) errors.push(`${where}: figure alt missing or under 10 characters`);
    if (!figure.caption || !String(figure.caption).trim()) errors.push(`${where}: figure has no caption`);
    if (figure.kind === 'interactive') {
      const explore = figure.explore;
      if (!explore?.image || !explore?.shares) errors.push(`${where}: an interactive figure needs explore.image and explore.shares`);
      else {
        if (!exists(folderOnDisk(explore.image))) errors.push(`${where}: missing explorer image ${explore.image}`);
        if (!exists(explore.shares)) errors.push(`${where}: missing explorer shares ${explore.shares}`);
      }
    }
  }

  const words = wordCount(body);
  if (!words) errors.push(`${where}: no Explain text (the file body)`);
  if (words > MAX_EXPLAIN_WORDS) errors.push(`${where}: Explain is ${words} words, over ${MAX_EXPLAIN_WORDS}`);
  if (!data.worked || !String(data.worked).trim()) errors.push(`${where}: no worked example`);

  errors.push(...questionErrors(`${where} predict`, data.predict));
  errors.push(...questionErrors(`${where} recall`, data.recall));
  // Recall asks a different case than the prediction (16 Nov 2026 test run), never the same question again.
  const norm = (q) => String(q ?? '').trim().replace(/\s+/g, ' ').toLowerCase();
  if (data.predict?.q && norm(data.predict.q) === norm(data.recall?.q)) errors.push(`${where}: recall repeats the prediction question; ask a different case`);

  const cites = Array.isArray(data.cite) ? data.cite : [];
  if (!cites.length) errors.push(`${where}: no citation`);
  for (const cite of cites) if (!parseCite(cite)) errors.push(`${where}: citation "${cite}" is not "Name & Name, 2018"`);
  // CT-2: each cite shows as a numbered marker in the text, <Cite c="Name & Name, 2018" />; no marker without a cite entry.
  const marked = citeMarkers(body);
  for (const mark of marked) if (!cites.includes(mark)) errors.push(`${where}: <Cite c="${mark}" /> is not in the cite list`);
  for (const cite of cites) {
    if (!marked.includes(cite)) errors.push(`${where}: citation "${cite}" has no <Cite c="${cite}" /> marker in the text`);
    if (String(body).includes(`(${cite})`)) errors.push(`${where}: write "${cite}" as a <Cite> marker, not in brackets (CT-2)`);
  }
  return errors;
}

const SCREEN_TAGS = ['MakeItFirst', 'ConceptScreen', 'TryStep', 'Step', 'MakeItYours', 'TryWrap', 'WrapUp'];
const TASK_TAGS = new Set(['TryStep', 'Step']);

function attr(attrs, name) {
  const quoted = attrs.match(new RegExp(`\\b${name}="([^"]*)"`));
  if (quoted) return quoted[1];
  const braced = attrs.match(new RegExp(`\\b${name}=\\{([^}]*)\\}`));
  return braced ? braced[1].trim() : undefined;
}

/** The screens of a lesson, in order: { tag, id, n, of, minutes, concept, recall }. */
export function parseLessonScreens(source) {
  const pattern = new RegExp(`<(${SCREEN_TAGS.join('|')})\\b([^>]*)>`, 'g');
  const screens = [];
  for (const [, tag, attrs] of String(source).matchAll(pattern)) {
    const minutes = attr(attrs, 'minutes');
    const recall = attr(attrs, 'recall');
    screens.push({
      tag,
      id: attr(attrs, 'id'),
      n: Number(attr(attrs, 'n')) || undefined,
      of: Number(attr(attrs, 'of')) || undefined,
      minutes: minutes === undefined ? (tag === 'MakeItFirst' ? 3 : undefined) : Number(minutes),
      concept: attr(attrs, 'concept'),
      recall: recall ? [...recall.matchAll(/["']([\w-]+)["']/g)].map((m) => m[1]) : undefined,
    });
  }
  return screens;
}

/** The c="…" values of the <Cite c="…" /> markers in a text, in order. */
export function citeMarkers(text) {
  return [...String(text ?? '').matchAll(/<Cite\s+c="([^"]*)"\s*\/>/g)].map((m) => m[1]);
}

/** The step blocks of a lesson: { n, source }, for the rules on a step's notes. */
function stepBlocks(source) {
  return [...String(source).matchAll(/<(TryStep|Step)\b([^>]*)>([\s\S]*?)<\/\1>/g)].map((m) => ({ n: attr(m[2], 'n'), source: m[3] }));
}

/** The <li> items of the lesson's References. */
export function referenceItems(source) {
  return [...String(source).matchAll(/<li>([\s\S]*?)<\/li>/g)].map((m) => m[1]);
}

/**
 * Rules on one lesson.
 * @param {{ file: string, lesson: string, source: string, public: boolean, budget: number }} lesson
 *   lesson: its id ("try"); a concept introduced in another lesson shows as an "Earlier" link.
 * @param {Map<string, { data: any }>} concepts  by id
 */
export function lessonErrors(lesson, concepts) {
  const where = lesson.file;
  const errors = [];
  const screens = parseLessonScreens(lesson.source);
  const conceptScreens = screens.filter((s) => s.tag === 'ConceptScreen');
  const tasks = screens.filter((s) => TASK_TAGS.has(s.tag));
  const usesConcepts = conceptScreens.length > 0 || tasks.some((s) => s.concept);
  if (!usesConcepts) return errors;

  if (conceptScreens.length > MAX_CONCEPT_SCREENS) {
    errors.push(`${where}: ${conceptScreens.length} concept screens, over ${MAX_CONCEPT_SCREENS} (FW-1)`);
  }

  // Unknown ids.
  const known = (id) => id && concepts.has(id);
  for (const s of conceptScreens) if (!known(s.id)) errors.push(`${where}: unknown concept id "${s.id}" on a concept screen`);
  for (const s of tasks) if (s.concept && !known(s.concept)) errors.push(`${where}: unknown concept id "${s.concept}" on step ${s.n}`);

  // Numbering: Concept n of N.
  conceptScreens.forEach((s, i) => {
    if (s.n !== i + 1 || s.of !== conceptScreens.length) {
      errors.push(`${where}: concept screen "${s.id}" must be n={${i + 1}} of={${conceptScreens.length}}`);
    }
  });

  // Condition 1: concept, task, concept, task; never before Make it first; never two in a row; a task after each.
  const firstIndex = screens.findIndex((s) => s.tag === 'MakeItFirst');
  screens.forEach((s, i) => {
    if (s.tag !== 'ConceptScreen') return;
    if (firstIndex >= 0 && i < firstIndex) errors.push(`${where}: concept "${s.id}" comes before Make it first (condition 1)`);
    const next = screens[i + 1];
    if (next?.tag === 'ConceptScreen') errors.push(`${where}: concepts "${s.id}" and "${next.id}" are in a row (condition 1)`);
    else if (!next || !TASK_TAGS.has(next.tag)) errors.push(`${where}: concept "${s.id}" has no task step after it (condition 1)`);
  });

  // Condition 3: every task step links back to its concept: a screen before it, or an Earlier link.
  screens.forEach((s, i) => {
    if (!TASK_TAGS.has(s.tag)) return;
    if (!s.concept) {
      errors.push(`${where}: step ${s.n} names no concept (condition 3)`);
      return;
    }
    const concept = concepts.get(s.concept);
    if (!concept) return;
    const screenBefore = screens.slice(0, i).some((b) => b.tag === 'ConceptScreen' && b.id === s.concept);
    const earlier = concept.data?.introduced?.lesson && concept.data.introduced.lesson !== lesson.lesson;
    if (!screenBefore && !earlier) errors.push(`${where}: step ${s.n} uses "${s.concept}" with no concept screen before it and no Earlier link (condition 3)`);
  });

  // FW-6: one interactive figure per lesson.
  const interactive = conceptScreens.filter((s) => concepts.get(s.id)?.data?.figure?.kind === 'interactive');
  if (interactive.length > 1) errors.push(`${where}: ${interactive.length} interactive figures, at most 1 (FW-6)`);

  // FW-3: Wrap up recalls one question per concept screen, in order.
  const wrap = screens.find((s) => s.tag === 'TryWrap' || s.tag === 'WrapUp');
  const recall = wrap?.recall ?? [];
  const order = conceptScreens.map((s) => s.id);
  if (recall.join(' ') !== order.join(' ')) {
    errors.push(`${where}: Wrap up recall [${recall.join(', ')}] must list the concept screens in order [${order.join(', ')}] (FW-3)`);
  }
  // TRB-2 (16 Nov 2026 test run): Wrap up is recall only, no own-words task (no <Task> inside Wrap up).
  const wrapBody = String(lesson.source).match(/<(TryWrap|WrapUp)\b[^>]*>([\s\S]*?)<\/\1>/);
  if (wrapBody && /<Task\b/.test(wrapBody[2])) errors.push(`${where}: Wrap up has a <Task>; Wrap up is recall only, no own-words question (TRB-2)`);

  // Minutes.
  const missing = screens.filter((s) => s.minutes === undefined || Number.isNaN(s.minutes));
  for (const s of missing) errors.push(`${where}: ${s.tag}${s.id ? ` "${s.id}"` : s.n ? ` ${s.n}` : ''} has no minutes`);
  const total = screens.reduce((sum, s) => sum + (s.minutes || 0), 0);
  if (total > lesson.budget) errors.push(`${where}: ${total} min, over the lesson budget of ${lesson.budget}`);

  // Citations in the lesson's References; gated figures never on a public page (TRB-3 a).
  const refs = referenceItems(lesson.source);
  const inRefs = (cite) => {
    const parsed = parseCite(cite);
    return Boolean(parsed) && refs.some((item) => item.includes(`(${parsed.year})`) && parsed.names.every((name) => item.includes(name)));
  };
  // CT-2: markers in the lesson's own text need a Sources entry; one numbered list, in Wrap up, nowhere else.
  for (const mark of citeMarkers(lesson.source)) if (!inRefs(mark)) errors.push(`${where}: <Cite c="${mark}" /> is not in the lesson's References`);
  if (usesConcepts) {
    const lists = [...lesson.source.matchAll(/<ol\b[^>]*\bdata-sources\b/g)];
    const wrapAt = lesson.source.search(/<(TryWrap|WrapUp)\b/);
    if (lists.length !== 1) errors.push(`${where}: ${lists.length} Sources lists (<ol data-sources>), exactly 1 (CT-2)`);
    else if (wrapAt < 0 || lists[0].index < wrapAt) errors.push(`${where}: the Sources list must be inside Wrap up, not on another screen (CT-2)`);
    const label = lesson.source.match(/label="Sources \((\d+)\)"/);
    if (label && Number(label[1]) !== refs.length) errors.push(`${where}: Sources label says ${label[1]}, the list has ${refs.length}`);
  }
  // SN-1: a step's Notes panel has at most a "Watch out" (before running) and a "Why it worked" (after a pass), each tied to a code line.
  if (lesson.public) {
    for (const step of stepBlocks(lesson.source)) {
      const tags = [...step.source.matchAll(/<Theory\b([^>]*)>/g)].map((m) => m[1]);
      const watch = tags.filter((t) => attr(t, 'slot') === 'theory');
      const worked = tags.filter((t) => attr(t, 'slot') === 'after');
      const name = `step ${step.n}`;
      if (tags.length > watch.length + worked.length) errors.push(`${where}: ${name} has a note in no known slot; use slot="theory" (Watch out) or slot="after" (Why it worked) (SN-1)`);
      if (watch.length > 1) errors.push(`${where}: ${name} has ${watch.length} Watch out notes, at most 1 (SN-1)`);
      if (worked.length > 1) errors.push(`${where}: ${name} has ${worked.length} Why it worked notes, at most 1 (SN-1)`);
      for (const t of watch) if (attr(t, 'title') !== 'Watch out') errors.push(`${where}: ${name} note before running must be titled "Watch out", not "${attr(t, 'title')}" (SN-1)`);
      for (const t of worked) if (attr(t, 'title') !== 'Why it worked') errors.push(`${where}: ${name} note after a pass must be titled "Why it worked", not "${attr(t, 'title')}" (SN-1)`);
      for (const t of [...watch, ...worked]) if (!attr(t, 'line')) errors.push(`${where}: ${name} note "${attr(t, 'title')}" names no code line (line="line 4"); a note must tie to the code (SN-1)`);
      if (worked.length && !/<Cell\b[^>]*\bcheck\b/.test(step.source)) errors.push(`${where}: ${name} has "Why it worked" but no check to open it after (SN-1)`);
    }
  }
  const used = new Set([...order, ...tasks.map((s) => s.concept)].filter((id) => known(id)));
  for (const id of used) {
    const data = concepts.get(id).data ?? {};
    for (const cite of data.cite ?? []) {
      if (!parseCite(cite)) continue;
      if (!inRefs(cite)) errors.push(`${where}: concept "${id}" cites "${cite}", which is not in the lesson's References`);
    }
    if (lesson.public && String(data.figure?.folder ?? '').startsWith('/workshop-media/')) {
      errors.push(`${where}: public page uses concept "${id}", whose figure is under /workshop-media/ (TRB-3 a)`);
    }
  }
  return errors;
}

/** The total minutes of a lesson, for the report. */
export function lessonMinutes(source) {
  return parseLessonScreens(source).reduce((sum, s) => sum + (s.minutes || 0), 0);
}
