/** Configure Vite's output and the Flask data proxy for webview development. */
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const pythonStaticOutput = fileURLToPath(
  new URL(
    "../proflow/analysis/webview/static/force/frontend-dist",
    import.meta.url,
  ),
);

export default defineConfig({
  base: "/force/frontend-dist/",
  build: {
    outDir: pythonStaticOutput,
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/data": "http://127.0.0.1:8000",
    },
  },
});
