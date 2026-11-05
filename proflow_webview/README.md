# Process network webview

This private Node ES-module package contains the isolated TypeScript frontend
for proFlow's process-network graph. It depends only on the JSON response
served at `/data`; it does not import Python modules or package code.

## Requirements

- Node.js 22 or newer
- pnpm (the committed `pnpm-lock.yaml` is used with `pnpm install --frozen-lockfile`)
- The proFlow Python environment with the optional Flask dependency to run the
  Flask host or browser tests

## Commands

Run these commands from the repository root:

```bash
pnpm --dir proflow_webview install --frozen-lockfile
pnpm --dir proflow_webview typecheck
pnpm --dir proflow_webview lint
pnpm --dir proflow_webview format:check
pnpm --dir proflow_webview test
pnpm --dir proflow_webview build
```

The Vite development server proxies the graph data endpoint to the Flask host
on port 8000. Install the optional Flask dependency with
`uv sync --locked --group web`, start the Python server with
`uv run --locked python -m proflow.analysis.webview.run_app`, then run
`pnpm --dir proflow_webview dev`.

The production build is written to
`proflow/analysis/webview/static/force/frontend-dist`. Commit generated
frontend assets with frontend source changes so source checkouts and Python
distributions can run the webview without Node.

Install Chromium once with
`pnpm --dir proflow_webview playwright:install`. The
`pnpm --dir proflow_webview test:e2e` command starts the Flask host and
exercises the webview in a browser. Vitest unit tests run with
`pnpm --dir proflow_webview test`.
