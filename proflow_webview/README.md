# Process network webview

This private Node ES-module package contains the isolated TypeScript frontend
for proFlow's process-network graph. It depends only on the JSON response
served at `/data`; it does not import Python modules or package code.

## Requirements

- Node.js 22 or newer
- npm (the committed `package-lock.json` is used with `npm ci`)
- The proFlow Python environment with the optional Flask dependency to run the
  Flask host or browser tests

## Commands

Run these commands from the repository root:

```bash
npm ci --prefix webview
npm --prefix webview run typecheck
npm --prefix webview run lint
npm --prefix webview run format:check
npm --prefix webview test
npm --prefix webview run build
```

The Vite development server proxies the graph data endpoint to the Flask host
on port 8000. Install the optional Flask dependency with
`uv sync --locked --group web`, start the Python server with
`uv run --locked python -m proflow.analysis.webview.run_app`, then run
`npm --prefix webview run dev`.

The production build is written to
`proflow/analysis/webview/static/force/frontend-dist`. Commit generated
frontend assets with frontend source changes so source checkouts and Python
distributions can run the webview without Node.

Install Chromium once with `npm --prefix webview run playwright:install`.
`npm --prefix webview run test:e2e` starts the Flask host and exercises the
webview in a browser. Vitest unit tests run with `npm --prefix webview test`.
