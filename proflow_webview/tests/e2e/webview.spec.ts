/** Exercise webview loading and user-facing graph controls in Chromium. */
import { expect, test } from "@playwright/test";

test("loads the graph and filters nodes and links", async ({ page }) => {
  await page.goto("/");

  const visibleNodes = page.locator("svg .node:visible");
  await expect(visibleNodes.first()).toBeVisible();
  const totalNodes = await visibleNodes.count();
  const search = page.getByRole("searchbox", { name: "Search nodes" });

  await search.fill("no node can match this query");
  await expect(visibleNodes).toHaveCount(0);
  await expect(page.locator("#filter-summary")).toHaveText(
    `0 of ${totalNodes} nodes shown`,
  );

  await search.fill("");
  await expect(visibleNodes).toHaveCount(totalNodes);
});

test("switches node shapes and pauses the force layout", async ({ page }) => {
  await page.goto("/");

  const boxOption = page.getByRole("radio", { name: "Box" });
  const dotOption = page.getByRole("radio", { name: "Dot" });
  await expect(boxOption).toBeChecked();
  await page.locator("svg .node rect").first().waitFor();

  await dotOption.check();
  await expect(page.locator("svg .node circle").first()).toBeVisible();
  await expect(page.locator("svg .node rect")).toHaveCount(0);

  const forceOption = page.getByRole("checkbox", { name: "Enable forces" });
  await forceOption.uncheck();
  await expect(forceOption).not.toBeChecked();
  await boxOption.check();
  const node = page.locator("svg .node").last();
  const bounds = await page.locator("svg .node rect").last().boundingBox();
  expect(bounds).not.toBeNull();
  if (!bounds) {
    throw new Error("The graph node has no browser bounding box.");
  }
  const beforeDrag = await node.getAttribute("transform");
  await page.mouse.move(
    bounds.x + bounds.width / 2,
    bounds.y + bounds.height / 2,
  );
  await page.mouse.down();
  await page.mouse.move(
    bounds.x + bounds.width / 2 + 40,
    bounds.y + bounds.height / 2 + 30,
  );
  await page.mouse.up();
  await expect(node).not.toHaveAttribute("transform", beforeDrag ?? "");
});

test("announces graph data failures accessibly", async ({ page }) => {
  await page.route("**/data", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ error: "unavailable" }),
    }),
  );

  await page.goto("/");

  await expect(page.getByRole("alert")).toContainText(
    "Unable to load process graph: Graph data request failed with status 503",
  );
});
