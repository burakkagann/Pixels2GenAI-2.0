import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';
import { inlineMarkdownText } from '@/lib/inlineMarkdown';

// RSS feed of every shipped lesson. Discovery + freshness signal for crawlers
// and a "new lesson" channel while the curriculum is ported module by module.
// Lessons carry no date field yet, so items are ordered by their numeric leaf
// id (1.1.1 < 1.2.1 < 2.1.1 …) rather than by pubDate.
export async function GET(context: APIContext) {
  const lessons = await getCollection('lessons');

  // Natural sort on the dotted numeric id ("2.1.1") so the feed reads in
  // curriculum order, not lexicographically ("10.1.1" before "2.1.1").
  const ordered = lessons.sort((a, b) => {
    const segs = (id: string) => id.split('.').map(Number);
    const [as, bs] = [segs(a.id), segs(b.id)];
    for (let i = 0; i < Math.max(as.length, bs.length); i++) {
      const diff = (as[i] ?? 0) - (bs[i] ?? 0);
      if (diff !== 0) return diff;
    }
    return 0;
  });

  return rss({
    title: 'Pixels2GenAI — Lessons',
    description:
      'New lessons from the Pixels2GenAI curriculum: from a single array element to building, training, and reasoning about modern generative models.',
    site: context.site!,
    items: ordered.map((lesson) => ({
      title: `${lesson.id} · ${lesson.data.title}`,
      description: inlineMarkdownText(lesson.data.objective),
      link: `/lessons/${lesson.id}`,
      // First-live date, so readers can sort and flag new lessons.
      ...(lesson.data.published ? { pubDate: lesson.data.published } : {}),
      categories: [lesson.data.module],
    })),
    // atom:link rel=self is what feed validators and some readers expect so
    // the feed can identify its own canonical URL.
    xmlns: { atom: 'http://www.w3.org/2005/Atom' },
    customData: `<language>en</language><atom:link href="${new URL('/feed.xml', context.site).href}" rel="self" type="application/rss+xml"/>`,
  });
}
