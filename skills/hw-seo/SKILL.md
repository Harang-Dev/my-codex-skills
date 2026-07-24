---
name: hw-seo
description: Audit and improve SEO in the AlphaSquare Vite/Vue monorepo. Use when reviewing or changing robots.txt, sitemap.xml, crawl/index policy, canonical or social metadata, structured data, SEO-sensitive routes, or search discoverability for packages/desktop, packages/mobile, packages/alphachart, or packages/alphachart-guest.
---

# HW SEO

Use this local-only workflow. Do not run, install, copy, or invoke code from external SEO skills. Do not access credential files, configure third-party APIs, submit URLs, request indexing, or change production services unless the user explicitly asks.

## Establish scope

1. Identify the target app and environment. This monorepo contains four web surfaces: `packages/desktop`, `packages/mobile`, `packages/alphachart`, and `packages/alphachart-guest`.
2. Inspect the target app's `public/robots.txt`, `public/sitemap.xml` when present, `vite.config.js`, and the shared staging override at `scripts/vite/createRobotsTxtPlugin.js`.
3. Treat authentication, account, payment, trading, portfolio, and user-specific pages as non-indexable by default. Do not remove an existing disallow rule without explaining the exposure risk and obtaining direction.
4. For claims about a deployed URL, inspect the supplied URL and label observations as either source-level or deployment-level. A Vite SPA build can differ from source and client-injected tags may not be reliably visible to crawlers.

## Audit

Report findings as `Critical`, `High`, `Medium`, or `Low`, with evidence and the exact affected path. Prefer a short, actionable report over a generic score.

Check these areas:

- **Environment protection:** staging builds must emit `User-agent: *` and `Disallow: /`; production crawler policy must be intentional.
- **Crawler policy:** validate directives, case, path scope, and that sensitive routes are disallowed. Do not interpret `robots.txt` as access control.
- **Sitemaps:** validate XML syntax and URLs; include only canonical, indexable, public routes. Follow sitemap indexes to their published files when the task includes live verification.
- **Metadata:** verify title, description, canonical, Open Graph, and Twitter tags for public landing and content routes. Do not claim a tag exists solely because a client-side component may render it.
- **Structured data:** use only data that accurately reflects visible content. Validate JSON-LD against Schema.org semantics; avoid fabricated review, FAQ, financial-performance, or product data.
- **Rendering and routing:** identify routes that return identical HTML or client-only metadata, redirect loops, soft-404 behavior, and publicly indexable error or account pages.
- **Performance:** inspect existing build output or user-provided measurements before recommending a performance fix. State whether data is lab, field, or inferred; do not invent Core Web Vitals values.

Read [repository-seo-map.md](references/repository-seo-map.md) for the known current layout and project-specific checks.

## Implement

Make the smallest change that satisfies the request.

- Preserve the existing Vite build pattern and use `@as/modules` for shared functionality rather than duplicating code per app.
- Keep staging crawl blocking in the shared plugin effective for every app that imports it.
- Update sitemap and robots files together when a route's indexability changes.
- Never expose private user, trading, account, analytics, API, or staging URLs through metadata, structured data, or sitemaps.
- For investment-related content, preserve existing compliance wording and do not add performance promises or unverified financial claims.

## Verify

After a source change:

1. Re-read the changed public files and configuration.
2. Run the narrowest relevant build or test command when dependencies are available.
3. Inspect the generated `robots.txt` for a staging build if the crawl policy changed.
4. Validate changed XML or JSON-LD syntactically.
5. Report what was verified, what was not, and any deployment-only checks still required.

Do not create reports, caches, browser profiles, credential files, or external-service configuration in the repository unless the user explicitly requests them.
