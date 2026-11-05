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

test("zooms and pans the graph without moving the control panel", async ({
  page,
}) => {
  await page.goto("/");

  const graph = page.locator("svg .graph-content");
  const controls = page.locator(".control-panel");
  const controlBoundsBefore = await controls.boundingBox();
  await page.getByRole("button", { name: "Zoom in" }).click();
  await expect(graph).toHaveAttribute("transform", /scale\(1\.2\)/);

  await page.getByRole("checkbox", { name: "Enable forces" }).uncheck();
  const node = page.locator("svg .node").last();
  const nodeBounds = await node.boundingBox();
  expect(nodeBounds).not.toBeNull();
  if (!nodeBounds) {
    throw new Error("The graph node has no browser bounding box.");
  }
  const nodeTransformBeforeDrag = await node.getAttribute("transform");
  await page.mouse.move(
    nodeBounds.x + nodeBounds.width / 2,
    nodeBounds.y + nodeBounds.height / 2,
  );
  await page.mouse.down();
  await page.mouse.move(
    nodeBounds.x + nodeBounds.width / 2 + 30,
    nodeBounds.y + nodeBounds.height / 2 + 20,
  );
  await page.mouse.up();
  await expect(node).not.toHaveAttribute(
    "transform",
    nodeTransformBeforeDrag ?? "",
  );

  const scaleBeforeWheel = await graph.evaluate((element) => {
    const match = element.getAttribute("transform")?.match(/scale\(([^)]+)\)/);
    if (!match) {
      throw new Error("The graph has no zoom scale.");
    }
    return Number(match[1]);
  });
  const svgBounds = await page.locator("svg").boundingBox();
  expect(svgBounds).not.toBeNull();
  if (!svgBounds) {
    throw new Error("The graph has no browser bounding box.");
  }
  await page.mouse.move(
    svgBounds.x + svgBounds.width * 0.8,
    svgBounds.y + svgBounds.height * 0.8,
  );
  await page.mouse.wheel(0, -120);

  await expect
    .poll(() =>
      graph.evaluate((element) => {
        const match = element
          .getAttribute("transform")
          ?.match(/scale\(([^)]+)\)/);
        return match ? Number(match[1]) : 1;
      }),
    )
    .toBeGreaterThan(scaleBeforeWheel);
  await page.mouse.wheel(0, -100000);
  await expect(graph).toHaveAttribute("transform", /scale\(4\)/);

  await page.getByRole("button", { name: "Reset" }).click();
  await expect(graph).toHaveAttribute("transform", /scale\(1\)/);
  const transformBeforePan = await graph.getAttribute("transform");
  await page.mouse.move(
    svgBounds.x + svgBounds.width * 0.9,
    svgBounds.y + svgBounds.height * 0.9,
  );
  await page.mouse.down();
  await page.mouse.move(
    svgBounds.x + svgBounds.width * 0.9 - 40,
    svgBounds.y + svgBounds.height * 0.9 - 30,
  );
  await page.mouse.up();
  await expect(graph).not.toHaveAttribute(
    "transform",
    transformBeforePan ?? "",
  );

  const controlBoundsAfter = await controls.boundingBox();
  expect(controlBoundsAfter).toEqual(controlBoundsBefore);
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
