# Publishing

## Python package

Build and publish the `repo-memory-mcp-ai` package to PyPI first. The official MCP Registry stores metadata and points to a public package; it does not host package artifacts.

```bash
python -m build
python -m twine upload dist/*
```

The PyPI package README must retain this ownership marker:

```text
mcp-name: io.github.Umarjaum/repo-memory-mcp
```

## Official MCP Registry

Install the official `mcp-publisher` CLI from the [MCP Registry releases](https://github.com/modelcontextprotocol/registry/releases), validate the metadata, authenticate with GitHub, and publish:

```bash
mcp-publisher validate
mcp-publisher login github
mcp-publisher publish
```

The GitHub namespace `io.github.Umarjaum/` requires authentication as the matching GitHub account. Registry publishing is intentionally not run automatically because it requires an interactive login and an already-public PyPI package.

The Registry is currently in preview. Published versions are immutable and unpublishing is not currently supported.

## Cloudflare Pages

The repository includes `.github/workflows/cloudflare-pages.yml`. It deploys the `website/` directory on every push to `main` using the Pages project name `repo-memory-mcp`; the site is static and requires no build command. The workflow needs two GitHub Actions secrets: `CLOUDFLARE_API_TOKEN` with Pages deployment permission and `CLOUDFLARE_ACCOUNT_ID`. Wrangler creates the Pages project on the first deployment when the token has the required account permissions. Update the canonical URL and sitemap URL in `website/index.html` and `website/robots.txt` if a custom domain is attached.

## GitHub Actions

The included test workflow runs on pushes and pull requests. Create a GitHub release only after the public package and repository URLs are final.

Sources: [MCP Registry about](https://modelcontextprotocol.io/registry/about), [official quickstart](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx), [FAQ](https://modelcontextprotocol.io/registry/faq).

## Repository publishing checklist

1. Push the repository to GitHub with public source, README, tests, and license.
2. Publish `repo-memory-mcp-ai` to PyPI.
3. Validate and publish `server.json` with `mcp-publisher`.
4. Connect the GitHub repository to Cloudflare Pages with `website/` as the output directory.
5. Replace placeholder canonical URLs after Pages assigns the final project URL or custom domain.
