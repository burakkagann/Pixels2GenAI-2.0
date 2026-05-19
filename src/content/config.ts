import { defineCollection, z } from 'astro:content';

const lessons = defineCollection({
  type: 'content',
  schema: z.object({
    /** Display label, e.g. "M 04". */
    module: z.string(),
    /** Cycle: I (foundations) | II (advanced) | III (AI/ML). */
    cycle: z.enum(['I', 'II', 'III']).default('I'),
    title: z.string(),
    /** One-sentence italic lead under the H1. */
    objective: z.string(),
    framework: z.enum(['hands-on', 'conceptual', 'hybrid', 'project']),
    duration: z.string(),
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
  }),
});

export const collections = { lessons };
