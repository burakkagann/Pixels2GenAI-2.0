/**
 * GitHub repo stats, fetched once at build time.
 *
 * FrameTop renders on every page, so the fetch is memoised at module scope:
 * Vite evaluates this module once per build and shares it across all pages,
 * giving us a single unauthenticated API call instead of one per route.
 *
 * The star count is therefore baked into the static HTML and refreshes on
 * each deploy (Netlify rebuilds on push). If the API is unreachable, the
 * fetch resolves to null and the caller simply omits the badge.
 */

/** Repo whose stars are shown next to the header "GitHub" link. Keep this in
 *  sync with the GitHub href in FrameTop.astro / Footer.astro. */
export const GITHUB_REPO = 'burakkagann/Pixels2GenAI';

let cached: Promise<number | null> | undefined;

export function getStarCount(): Promise<number | null> {
  if (!cached) {
    cached = fetch(`https://api.github.com/repos/${GITHUB_REPO}`, {
      headers: { Accept: 'application/vnd.github+json' },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) =>
        data && typeof data.stargazers_count === 'number'
          ? (data.stargazers_count as number)
          : null,
      )
      .catch(() => null);
  }
  return cached;
}

/** Compact star count for the badge: 1234 → "1.2k", 999 → "999". */
export function formatStars(n: number): string {
  if (n < 1000) return String(n);
  return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
}
