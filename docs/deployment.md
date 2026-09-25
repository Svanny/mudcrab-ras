# GitHub Pages deployment

Live site: <https://svanny.github.io/mudcrab-ras/>

The repository is public. GitHub Pages uses **GitHub Actions** as its build source. The `Validate and deploy Pages` workflow installs locked dependencies, runs data/geometry tests, creates the CAD download, builds the static site, checks the transfer-size budget, and deploys the `dist/` artifact. PRs validate without deploying; successful pushes to `main` deploy automatically.

No personal access token is stored in the repository. The deployment job receives only `pages:write` and `id-token:write`, with read-only repository contents. Action revisions are pinned; Dependabot proposes updates monthly.

## Deploy a fork

1. Create a public fork.
2. Enable Actions and set **Settings → Pages → Source → GitHub Actions**.
3. Update source/license links in `index.html` and live links in the README for your account/repository.
4. Run the workflow from **Actions**, or push to `main`.

Vite uses a relative base (`./`) so the build works under a project Pages prefix or a custom domain. The explorer uses a URL hash for route state, avoiding server-side routing and subpath 404s.

To configure a custom domain, use the repository's Pages settings, configure its DNS records, then enable HTTPS when the certificate is ready. No custom domain is assumed by the initial deployment.

## Rebuild and roll back

Use the workflow's **Run workflow** action to rebuild the current `main` revision. To roll back, revert the relevant commit on `main`; the workflow redeploys that state. Check the workflow run and the `github-pages` deployment environment for status.

## Asset transport

`equipment.mesh` is a gzip payload with a neutral filename. The browser explicitly decodes it with `DecompressionStream('gzip')`. Avoid renaming it to `.gz`: some static servers automatically set `Content-Encoding: gzip`, causing a second decode attempt. Export and binary integrity tests cover the format. Assets use Vite content hashes so new revisions receive new URLs.

The CAD package is a separate, on-demand 317 KiB download. No GIF/video or original reference document is loaded by the website.

References: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [Vite static deployment](https://vite.dev/guide/static-deploy).
