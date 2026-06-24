// Server-side GitHub star-count proxy (Netlify Functions v2).
//
// The header/footer show a live star count. Doing that fetch in the browser
// would send every visitor's IP to GitHub (a US third party) on every page —
// so instead the browser calls this same-origin function and GitHub only ever
// sees Netlify's server IP. The response is edge-cached for an hour, so across
// all visitors GitHub is hit at most ~once/hour (well within rate limits).
//
// Optional: set a GITHUB_TOKEN env var in the Netlify UI to lift the 60/hr
// unauthenticated limit. It stays server-side and is never exposed to clients.

const REPO = 'burakkagann/Pixels2GenAI-2.0';

function json(body, sMaxAge) {
  return new Response(JSON.stringify(body), {
    headers: {
      'Content-Type': 'application/json',
      // Browser revalidates; Netlify's edge serves a cached copy for s-maxage.
      'Cache-Control': `public, max-age=0, s-maxage=${sMaxAge}`,
    },
  });
}

export default async function handler() {
  const headers = {
    Accept: 'application/vnd.github+json',
    'User-Agent': 'pixels2genai-site',
  };
  if (process.env.GITHUB_TOKEN) {
    headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  }
  try {
    const res = await fetch(`https://api.github.com/repos/${REPO}`, { headers });
    if (!res.ok) return json({ stars: null }, 300); // back off briefly on error
    const data = await res.json();
    const stars =
      typeof data.stargazers_count === 'number' ? data.stargazers_count : null;
    return json({ stars }, 3600);
  } catch {
    return json({ stars: null }, 300);
  }
}
