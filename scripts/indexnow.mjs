#!/usr/bin/env node
/**
 * IndexNow submitter — pings the IndexNow API (Bing, Yandex, Naver, Seznam,
 * Yep) so changed URLs are picked up near-instantly instead of waiting for a
 * crawl. Bing feeds Microsoft Copilot, so this is the highest-leverage
 * freshness signal for the AI-answer surface. (Google does not support
 * IndexNow.)
 *
 * Run AFTER a production deploy is live, since it reads the deployed sitemap:
 *
 *   npm run indexnow                      # submit every URL in the live sitemap
 *   npm run indexnow -- https://pixels2genai.art/lessons/7.1.1/   # submit specific URLs
 *
 * The key file (public/<KEY>.txt) must be deployed and reachable at KEY_LOCATION
 * for submissions to be accepted.
 */

const HOST = 'pixels2genai.art';
const SITE = `https://${HOST}`;
const KEY = 'f9daa1632f3d44ecabe8051c47dbc84b';
const KEY_LOCATION = `${SITE}/${KEY}.txt`;
const SITEMAP_INDEX = `${SITE}/sitemap-index.xml`;
const ENDPOINT = 'https://api.indexnow.org/indexnow';

/** Pull every <loc> value out of a sitemap XML string. */
function extractLocs(xml) {
  return [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/g)].map((m) => m[1]);
}

async function fetchText(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${url}`);
  return res.text();
}

/** Collect all page URLs from the sitemap index (following child sitemaps). */
async function collectSitemapUrls() {
  const indexXml = await fetchText(SITEMAP_INDEX);
  const locs = extractLocs(indexXml);
  const childSitemaps = locs.filter((u) => u.endsWith('.xml'));
  const directPages = locs.filter((u) => !u.endsWith('.xml'));

  const pages = new Set(directPages);
  for (const sm of childSitemaps) {
    const xml = await fetchText(sm);
    for (const loc of extractLocs(xml)) {
      if (!loc.endsWith('.xml')) pages.add(loc);
    }
  }
  return [...pages];
}

async function main() {
  const cliUrls = process.argv.slice(2).filter((a) => a.startsWith('http'));

  let urlList;
  if (cliUrls.length) {
    urlList = cliUrls;
    console.log(`Submitting ${urlList.length} URL(s) from the command line.`);
  } else {
    urlList = await collectSitemapUrls();
    console.log(`Submitting ${urlList.length} URL(s) from ${SITEMAP_INDEX}.`);
  }

  if (!urlList.length) {
    console.error('No URLs to submit — aborting.');
    process.exit(1);
  }

  const res = await fetch(ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ host: HOST, key: KEY, keyLocation: KEY_LOCATION, urlList }),
  });

  // IndexNow returns 200 (accepted) or 202 (accepted, pending validation).
  if (res.ok) {
    console.log(`IndexNow accepted the submission (HTTP ${res.status}).`);
  } else {
    const body = await res.text().catch(() => '');
    console.error(`IndexNow rejected the submission (HTTP ${res.status}). ${body}`.trim());
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(`IndexNow submission failed: ${err.message}`);
  process.exit(1);
});
