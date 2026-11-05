/** Verify validation and fetching at the Python-to-frontend graph boundary. */
import { describe, expect, it } from "vitest";
import {
  fetchGraphData,
  GraphDataError,
  parseGraphData,
} from "../src/graph-data";

const validPayload = {
  directed: true,
  multigraph: true,
  graph: {},
  nodes: [{ id: 1, x: 0, y: 0, name: "process", text: "description" }],
  links: [{ source: 1, target: 1, name: "state", key: 0, id: 1 }],
};

describe("parseGraphData", () => {
  it("accepts graph JSON matching the Python export contract", () => {
    expect(parseGraphData(validPayload)).toEqual({
      nodes: [{ id: 1, x: 0, y: 0, name: "process", text: "description" }],
      links: [{ source: 1, target: 1, name: "state", key: 0, id: 1 }],
    });
  });

  it("rejects malformed node records", () => {
    expect(() =>
      parseGraphData({
        ...validPayload,
        nodes: [{ id: "1", name: "process", text: "description" }],
      }),
    ).toThrow(GraphDataError);
  });

  it("rejects links whose endpoint is not a known node", () => {
    expect(() =>
      parseGraphData({
        ...validPayload,
        links: [{ source: 1, target: 2, name: "state", key: 0, id: 1 }],
      }),
    ).toThrow(/unknown node/);
  });

  it("reports unsuccessful graph-data requests", async () => {
    const fetcher: typeof fetch = async () =>
      new Response(JSON.stringify({ error: "unavailable" }), { status: 503 });

    await expect(fetchGraphData("/data", fetcher)).rejects.toThrow(
      "Graph data request failed with status 503",
    );
  });
});
