/** Configure Chromium browser tests against the Flask-hosted webview. */
import { fileURLToPath } from "node:url";
import { defineConfig, devices } from "@playwright/test";

const repositoryRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:8765",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command:
      "uv run --locked --no-sync python -m proflow.analysis.webview.run_app",
    cwd: repositoryRoot,
    url: "http://127.0.0.1:8765",
    reuseExistingServer: false,
    timeout: 30_000,
    env: {
      PROFLOW_WEBVIEW_PORT: "8765",
    },
  },
});
