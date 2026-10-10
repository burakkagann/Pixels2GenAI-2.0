import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const lessons = defineCollection({
  loader: glob({
    pattern: '**/*.mdx',
    base: './src/content/lessons',
    // The numeric leaf id is the lesson's stable identity and its URL slug:
    // "Module_02_geometry_mathematics/2.1_basic_shapes_primitives/2.1.1_lines.mdx" → "2.1.1".
    // Depth-agnostic so the collection keeps building mid-reorganization.
    generateId: ({ entry }) => {
      const match = entry.split('/').pop()!.match(/^(\d+(?:\.\d+)*)/);
      if (!match) throw new Error(`Lesson filename must start with a numeric id: ${entry}`);
      return match[1];
    },
  }),
  schema: z.object({
    /** Display label, e.g. "M 04". */
    module: z.string(),
    /** Cycle: I (foundations) | II (advanced) | III (AI/ML). */
    cycle: z.enum(['I', 'II', 'III']).default('I'),
    title: z.string(),
    /** One-sentence italic lead under the H1. */
    objective: z.string(),
    /** Optional search-snippet text (<= 160 chars) for meta/og descriptions.
     *  Omitted: the objective, trimmed to fit (src/lib/metaDescription.ts). */
    description: z.string().optional(),
    framework: z.enum(['hands-on', 'conceptual', 'hybrid', 'project']),
    duration: z.string(),
    /** Date the lesson first went live (v1 deploy date for ported lessons).
     *  Feeds RSS pubDate and LearningResource datePublished. */
    published: z.coerce.date().optional(),
    level: z.enum([
      'beginner',
      'beginner-intermediate',
      'intermediate',
      'intermediate-advanced',
      'advanced',
    ]),
    /** Optional: cognitive-load chip (e.g. "3 new concepts"). */
    load: z.string().optional(),
    /** Optional: prerequisites chip. */
    prereqs: z.string().optional(),
    /** Sibling-lesson navigation. Null when at the boundary. */
    prev: z
      .object({ slug: z.string(), title: z.string() })
      .nullable()
      .default(null),
    next: z
      .object({ slug: z.string(), title: z.string() })
      .nullable()
      .default(null),
    /** Back-link to the module/topic page. Falls back to landing /#curriculum. */
    backLink: z.object({ href: z.string(), label: z.string() }).optional(),
    /**
     * Optional FAQ pairs, emitted as FAQPage JSON-LD for rich results / AI
     * citation. Only add entries whose Q&A is ALSO visible on the page (e.g.
     * mirrors the reflection questions and their answer dropdowns) — Google
     * requires FAQ markup to reflect on-page content.
     */
    faq: z
      .array(z.object({ q: z.string(), a: z.string() }))
      .optional(),
  }),
});

// Workshop-area lessons (lesson framework v2). A separate collection on
// purpose: RSS, llms.txt, OG images, /lessons/[slug] and the lesson JSON-LD all
// read getCollection('lessons') by name, so nothing here can leak into them.
// Pages for it are only routed when PUBLIC_WORKSHOP_AREA=true (astro.config.mjs).
// Layout: src/content/workshop-lessons/<workshop slug>/<lesson id>_<name>.mdx
const workshopLessons = defineCollection({
  loader: glob({
    pattern: '*/*.mdx',
    base: './src/content/workshop-lessons',
    // "w1-see/3.4.1_convolution.mdx" → "w1-see/3.4.1": the URL path under
    // /workshops. Its own rule, so it can never trip the lessons generateId.
    generateId: ({ entry }) => {
      const [workshop, file] = entry.split('/');
      const match = file?.match(/^(\d+(?:\.\d+)*)/);
      if (!/^w[1-6]-[a-z]+$/.test(workshop ?? '') || !match) {
        throw new Error(`Workshop lesson must live at <w1-see>/<id>_<name>.mdx: ${entry}`);
      }
      return `${workshop}/${match[1]}`;
    },
  }),
  // Minimal for now; the framework v2 fields arrive with the lesson port (BLD-02).
  schema: z.object({
    title: z.string(),
    objective: z.string(),
    duration: z.string(),
    level: z.enum([
      'beginner',
      'beginner-intermediate',
      'intermediate',
      'intermediate-advanced',
      'advanced',
    ]),
  }),
});

export const collections = { lessons, workshopLessons };
