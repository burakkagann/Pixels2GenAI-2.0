import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';
import { MODULES, moduleIndexFromLabel } from '@/data/curriculum/modules';

// /llms.txt — a curated, low-token map of the curriculum for LLMs and AI
// answer engines (the llmstxt.org convention). Generated from the shipped-lesson
// collection so it stays current as modules are ported. This complements
// robots.txt + the sitemap; major providers do not yet consume llms.txt, so
// treat it as a low-cost, forward-looking hint, not a primary discovery channel.
export async function GET(context: APIContext) {
  const site = context.site!.origin;
  const lessons = await getCollection('lessons');

  // Natural sort on the dotted id ("2.1.1") so lessons read in curriculum order.
  const segs = (id: string) => id.split('.').map(Number);
  const ordered = lessons.sort((a, b) => {
    const [as, bs] = [segs(a.id), segs(b.id)];
    for (let i = 0; i < Math.max(as.length, bs.length); i++) {
      const diff = (as[i] ?? 0) - (bs[i] ?? 0);
      if (diff !== 0) return diff;
    }
    return 0;
  });

  const moduleHeading = (label: string) => {
    const idx = moduleIndexFromLabel(label);
    const m = MODULES.find((mod) => parseInt(mod.idx, 10) === idx);
    return m ? `Module ${m.idx} — ${m.title} ${m.em}` : label;
  };

  const lines: string[] = [];
  lines.push('# Pixels2GenAI');
  lines.push('');
  lines.push(
    '> A free, open-source curriculum that takes a learner from a single array ' +
      'element to building, training, and reasoning about modern generative models, ' +
      'across fifteen progressive modules and a capstone. Developed as a Master’s ' +
      'thesis using Design-Based Research.',
  );
  lines.push('');
  lines.push(
    'Pixels2GenAI teaches generative art and AI through hands-on, visual-first ' +
      'lessons (roughly 40% theory, 60% practice) using a progressive ' +
      'Execute → Modify → Create scaffold. Each lesson includes runnable Python, ' +
      'diagrams and output figures, cited references (APA 7th edition), and reflection ' +
      'questions. The lessons below are the chapters published so far; the curriculum ' +
      'is ported module by module.',
  );
  lines.push('');

  let currentModule = '';
  for (const lesson of ordered) {
    const heading = moduleHeading(lesson.data.module);
    if (heading !== currentModule) {
      currentModule = heading;
      lines.push('');
      lines.push(`## ${heading}`);
    }
    const objective = (lesson.data.objective ?? '').trim().replace(/\s+/g, ' ');
    lines.push(
      `- [${lesson.id} ${lesson.data.title}](${site}/lessons/${lesson.id})` +
        (objective ? `: ${objective}` : ''),
    );
  }

  lines.push('');
  lines.push('## Project');
  lines.push('');
  lines.push(
    `- [Research and methodology](${site}/research): the thesis framing, research ` +
      'questions, and Design-Based Research methodology behind the curriculum.',
  );
  lines.push(
    `- [Workshops](${site}/workshops): the full curriculum delivered as a one-day workshop.`,
  );
  lines.push(
    `- [Exhibition](${site}/exhibitions/2026-03): generative prints produced with the ` +
      'techniques taught in the modules.',
  );
  lines.push('');
  lines.push('## Optional');
  lines.push('');
  lines.push(`- [RSS feed of new lessons](${site}/feed.xml)`);
  lines.push(`- [XML sitemap](${site}/sitemap-index.xml)`);
  lines.push('');

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
