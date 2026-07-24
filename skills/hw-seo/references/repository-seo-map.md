# AlphaSquare SEO map

Use this map as a starting point and re-check it before making changes.

| Surface | Crawl policy | Sitemap | Build integration |
| --- | --- | --- | --- |
| `packages/desktop` | `public/robots.txt` disallows `/stock/trading-note` | `public/sitemap.xml` is a sitemap index pointing to `https://file.alphasquare.co.kr/static/sitemap.xml` | imports the shared robots plugin |
| `packages/mobile` | `public/robots.txt` disallows `/account` and `/service/user-setting` | no local sitemap found | imports the shared robots plugin |
| `packages/alphachart` | `public/robots.txt` permits named crawlers | no local sitemap found | imports the shared robots plugin |
| `packages/alphachart-guest` | `public/robots.txt` permits named crawlers | no local sitemap found | imports the shared robots plugin |

`scripts/vite/createRobotsTxtPlugin.js` writes a full-disallow `robots.txt` only when Vite mode is `staging`. It is imported by the four Vite applications above.

Current source scanning found no established shared SEO metadata helper or canonical/JSON-LD implementation. Confirm the rendered production HTML before adding one; Vite applications are client-rendered unless another delivery layer changes that behavior.

## Quick source checks

```sh
rg -n -i '(canonical|robots|sitemap|json-ld|schema\.org|og:|twitter:|useHead|metaInfo)' packages scripts
rg --files packages -g 'robots.txt' -g 'sitemap*.xml' -g 'vite.config.*'
```

## Important interpretation rules

- `robots.txt` directs cooperative crawlers but does not prevent direct access or guarantee deindexing.
- A sitemap lists preferred discovery URLs; it does not make a page indexable.
- Crawlers need public, stable HTML and canonical signals. Client-side changes need deployed-page verification.
