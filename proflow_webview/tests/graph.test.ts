/** Verify graph filtering and SVG geometry helpers independently of the DOM. */
import { describe, expect, it } from "vitest";
import {
  bezierPath,
  getVisibleNodeIds,
  matchesNode,
  nodeBoundaryPoints,
} from "../src/graph";
import type { GraphLink, GraphNode } from "../src/graph-data";

const source: GraphNode = {
  id: 1,
  x: 0,
  y: 0,
  name: "producer",
  text: "writes state",
};
const target: GraphNode = {
  id: 2,
  x: 300,
  y: 100,
  name: "consumer",
  text: "reads state",
};
const link: GraphLink = {
  source,
  target,
  name: "state.value",
  key: 0,
  id: 1,
  linkindex: 1,
};

describe("node filtering", () => {
  it("matches node IDs, names, and descriptions without regard to case", () => {
    expect(matchesNode(source, "PRODUCER")).toBe(true);
    expect(matchesNode(source, "writes")).toBe(true);
    expect(matchesNode(source, "1")).toBe(true);
    expect(matchesNode(source, "absent")).toBe(false);
  });

  it("returns only IDs matching the trimmed query", () => {
    expect(getVisibleNodeIds([source, target], " consumer ")).toEqual(
      new Set([2]),
    );
    expect(getVisibleNodeIds([source, target], "")).toEqual(new Set([1, 2]));
  });
});

describe("link geometry", () => {
  it("connects box links to their left and right edges", () => {
    expect(nodeBoundaryPoints(link, "box")).toEqual({
      source: { x: 90, y: 0 },
      target: { x: 210, y: 100 },
    });
  });

  it("connects dot links to their circumference", () => {
    const points = nodeBoundaryPoints(link, "dot");
    const sourceDistance = Math.hypot(
      points.source.x - source.x!,
      points.source.y - source.y!,
    );
    const targetDistance = Math.hypot(
      points.target.x - target.x!,
      points.target.y - target.y!,
    );

    expect(sourceDistance).toBeCloseTo(5);
    expect(targetDistance).toBeCloseTo(5);
  });

  it("uses horizontal endpoint tangents for box links", () => {
    const path = bezierPath(true, link, "box");

    expect(path).toBe("M90,0C240,0 60,100 210,100");
  });
});
