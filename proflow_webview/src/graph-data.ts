/** Define the typed graph contract shared with the Python JSON exporter. */
import type { SimulationLinkDatum, SimulationNodeDatum } from "d3";

/** Describe a process node and its mutable D3 force-layout coordinates. */
export interface GraphNode extends SimulationNodeDatum {
  id: number;
  x: number;
  y: number;
  name: string;
  text: string;
}

/** Describe a process link before or after D3 resolves endpoint IDs. */
export interface GraphLink extends SimulationLinkDatum<GraphNode> {
  source: number | GraphNode;
  target: number | GraphNode;
  name: string;
  key: number;
  id: number;
  linkindex?: number;
}

/** Describe the frontend subset of the Python-exported node-link document. */
export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

/** Signal that the graph response does not satisfy the frontend contract. */
export class GraphDataError extends Error {
  /** Create a graph contract validation error with a useful message. */
  constructor(message: string) {
    super(message);
    this.name = "GraphDataError";
  }
}

/** Check whether a JSON value is a non-null object record. */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Check whether a JSON value is an integer. */
function isInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value);
}

/** Validate graph data against the frontend contract. */
function validateGraphData(value: unknown): {
  nodes: unknown[];
  links: unknown[];
} {
  if (
    !isRecord(value) ||
    !Array.isArray(value.nodes) ||
    !Array.isArray(value.links)
  ) {
    throw new GraphDataError("Graph data must contain node and link arrays.");
  }
  return { nodes: value.nodes, links: value.links };
}

/** Validate a graph node against the frontend contract. */
function validateGraphNode(
  node: unknown,
  index: number,
): asserts node is GraphNode {
  if (
    !isRecord(node) ||
    !isInteger(node.id) ||
    typeof node.x !== "number" ||
    !Number.isFinite(node.x) ||
    typeof node.y !== "number" ||
    !Number.isFinite(node.y) ||
    typeof node.name !== "string" ||
    typeof node.text !== "string"
  ) {
    throw new GraphDataError(`Graph node at index ${index} is invalid.`);
  }
}

/** Validate a graph link against the frontend contract. */
function validateGraphLink(
  link: unknown,
  index: number,
  nodeIds: Set<number>,
): asserts link is GraphLink {
  if (
    !isRecord(link) ||
    !isInteger(link.source) ||
    !isInteger(link.target) ||
    !nodeIds.has(link.source) ||
    !nodeIds.has(link.target) ||
    typeof link.name !== "string" ||
    !isInteger(link.key) ||
    !isInteger(link.id)
  ) {
    throw new GraphDataError(
      `Graph link at index ${index} has an invalid or unknown node endpoint.`,
    );
  }
}

/**
 * Extract and validate graph nodes from the given graph data.
 * @param value The graph data containing nodes and links.
 * @returns An array of validated graph nodes.
 */
function getNodes(value: { nodes: unknown[]; links: unknown[] }): GraphNode[] {
  return value.nodes.map((node, index) => {
    validateGraphNode(node, index);
    return {
      id: node.id,
      x: node.x,
      y: node.y,
      name: node.name,
      text: node.text,
    };
  });
}

function getLinks(
  value: { nodes: unknown[]; links: unknown[] },
  nodeIds: Set<number>,
): GraphLink[] {
  return value.links.map((link, index) => {
    validateGraphLink(link, index, nodeIds);
    return {
      source: link.source,
      target: link.target,
      name: link.name,
      key: link.key,
      id: link.id,
    };
  });
}

/** Validate an unknown response and return the graph data used by D3. */
export function parseGraphData(value: unknown): GraphData {
  const validatedGraphData = validateGraphData(value);
  const nodes = getNodes(validatedGraphData);
  const nodeIds = new Set(nodes.map((node) => node.id));
  const links = getLinks(validatedGraphData, nodeIds);
  return { nodes, links };
}

/** Fetch and validate graph data from the webview's JSON endpoint. */
export async function fetchGraphData(
  url = "/data",
  fetcher: typeof fetch = fetch,
): Promise<GraphData> {
  const response = await fetcher(url);
  if (!response.ok) {
    throw new Error(
      `Graph data request failed with status ${response.status}.`,
    );
  }

  return parseGraphData(await response.json());
}
