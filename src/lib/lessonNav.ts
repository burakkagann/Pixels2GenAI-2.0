/**
 * Previous/Next lesson navigation, computed at build time.
 *
 * Neighbors are derived from curriculum order (MODULES order, then each
 * module's SUBTOPICS leaves in order), skipping every leaf whose lesson isn't
 * shipped yet. Navigation therefore never dead-ends on a "Coming soon" leaf,
 * crosses module boundaries, and picks up newly shipped lessons without any
 * frontmatter edits. The frontmatter `prev` / `next` fields are ignored for
 * cataloged lessons — scripts/check-lessons.mjs mirrors this rule.
 *
 * Kept free of astro:content imports so it stays a pure function of its inputs.
 */

import type { ModuleEntry } from '@/data/curriculum/modules';
import type { SubtopicEntry } from '@/data/curriculum/subtopics';

export interface NeighborLink {
  slug: string;
  title: string;
}

export interface LessonNav {
  prev: NeighborLink | null;
  next: NeighborLink | null;
}

/** Every wired lesson slug in reading order (module → subtopic → leaf). */
export function curriculumOrder(
  modules: readonly ModuleEntry[],
  subtopics: Record<string, SubtopicEntry[]>
): string[] {
  return modules.flatMap((m) =>
    (subtopics[m.idx] ?? []).flatMap((s) =>
      s.leaves.flatMap((leaf) => (leaf.lessonSlug ? [leaf.lessonSlug] : []))
    )
  );
}

/**
 * Nearest shipped lesson on each side of `slug` in `order`.
 *
 * `titles` maps every shipped lesson slug to its frontmatter title; a slug
 * missing from it counts as not shipped. A lesson that isn't in the
 * curriculum order at all (an MDX not yet wired into subtopics.ts) falls back
 * to its frontmatter neighbors, keeping only those that are shipped.
 */
export function lessonNav(
  slug: string,
  order: readonly string[],
  titles: ReadonlyMap<string, string>,
  fallback: LessonNav = { prev: null, next: null }
): LessonNav {
  const link = (target: string): NeighborLink => ({ slug: target, title: titles.get(target)! });
  const shipped = (target: string | undefined) => !!target && titles.has(target);

  const position = order.indexOf(slug);
  if (position === -1) {
    return {
      prev: fallback.prev && shipped(fallback.prev.slug) ? link(fallback.prev.slug) : null,
      next: fallback.next && shipped(fallback.next.slug) ? link(fallback.next.slug) : null,
    };
  }

  const before = order.slice(0, position).reverse().find(shipped);
  const after = order.slice(position + 1).find(shipped);
  return {
    prev: before ? link(before) : null,
    next: after ? link(after) : null,
  };
}
