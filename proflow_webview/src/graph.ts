/** Render and manage the interactive process graph using D3. */
import {
  drag,
  forceCenter,
  forceLink,
  forceManyBody,
  forceSimulation,
  select,
  scaleOrdinal,
  schemeCategory10,
  type Selection,
} from "d3";
import type { GraphData, GraphLink, GraphNode } from "./graph-data";

/** Define the node rendering modes supported by the control panel. */
export type NodeShape = "box" | "dot";

const NODE_WIDTH = 180;
const NODE_HEIGHT = 48;
const NODE_DOT_RADIUS = 5;

/** Return the graph node represented by a D3-resolved link endpoint. */
function endpointNode(endpoint: number | GraphNode): GraphNode {
  if (typeof endpoint === "number") {
    throw new Error("Graph link endpoints must be resolved before rendering.");
  }
  return endpoint;
}

/** Return an endpoint's numeric ID before or after D3 resolves the link. */
function endpointId(endpoint: number | GraphNode): number {
  return typeof endpoint === "number" ? endpoint : endpoint.id;
}

/** Match a node's ID, function name, or description against a search query. */
export function matchesNode(node: GraphNode, query: string): boolean {
  const normalizedQuery = query.trim().toLocaleLowerCase();
  return (
    normalizedQuery.length === 0 ||
    [node.id, node.name, node.text]
      .join(" ")
      .toLocaleLowerCase()
      .includes(normalizedQuery)
  );
}

/** Return all node IDs visible for the given search query. */
export function getVisibleNodeIds(
  nodes: GraphNode[],
  query: string,
): Set<number> {
  return new Set(
    nodes.filter((node) => matchesNode(node, query)).map((node) => node.id),
  );
}

/** Calculate link endpoints on the selected node shape's boundary. */
export function nodeBoundaryPoints(
  link: GraphLink,
  shape: NodeShape,
): { source: { x: number; y: number }; target: { x: number; y: number } } {
  const source = endpointNode(link.source);
  const target = endpointNode(link.target);
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const distance = Math.hypot(dx, dy);

  if (shape === "dot") {
    const offset = distance === 0 ? 0 : NODE_DOT_RADIUS / distance;
    return {
      source: { x: source.x + dx * offset, y: source.y + dy * offset },
      target: { x: target.x - dx * offset, y: target.y - dy * offset },
    };
  }

  return {
    source: { x: source.x + NODE_WIDTH / 2, y: source.y },
    target: { x: target.x - NODE_WIDTH / 2, y: target.y },
  };
}

/** Build a cubic Bézier path whose box endpoints have horizontal tangents. */
export function bezierPath(
  leftHand: boolean,
  link: GraphLink,
  shape: NodeShape,
): string {
  const endpoints = nodeBoundaryPoints(link, shape);
  const start = leftHand ? endpoints.source : endpoints.target;
  const end = leftHand ? endpoints.target : endpoints.source;
  const startNode = endpointNode(leftHand ? link.source : link.target);
  const endNode = endpointNode(leftHand ? link.target : link.source);
  const dx = endNode.x - startNode.x;
  const dy = endNode.y - startNode.y;
  const distance = Math.hypot(dx, dy) || 1;
  const controlDistance =
    Math.max(NODE_WIDTH / 2, Math.abs(dx) / 2) +
    ((link.linkindex ?? 1) - 1) * 12;

  const control1 =
    shape === "box"
      ? { x: start.x + (leftHand ? 1 : -1) * controlDistance, y: start.y }
      : {
          x: start.x + (dx / distance) * controlDistance,
          y: start.y + (dy / distance) * controlDistance,
        };
  const control2 =
    shape === "box"
      ? { x: end.x - (leftHand ? 1 : -1) * controlDistance, y: end.y }
      : {
          x: end.x - (dx / distance) * controlDistance,
          y: end.y - (dy / distance) * controlDistance,
        };

  return `M${start.x},${start.y}C${control1.x},${control1.y} ${control2.x},${control2.y} ${end.x},${end.y}`;
}

/** Sort links and assign stable offsets to parallel process dependencies. */
function sortAndIndexLinks(links: GraphLink[]): void {
  links.sort((left, right) => {
    const sourceDifference = endpointId(left.source) - endpointId(right.source);
    return (
      sourceDifference || endpointId(left.target) - endpointId(right.target)
    );
  });

  let previousPair = "";
  let pairIndex = 0;
  for (const link of links) {
    const pair = `${endpointId(link.source)},${endpointId(link.target)}`;
    pairIndex = pair === previousPair ? pairIndex + 1 : 1;
    link.linkindex = pairIndex;
    previousPair = pair;
  }
}

/** Render the graph and connect the search, shape, force, and drag controls. */
export function renderGraph(graph: GraphData): void {
  const svgElement = document.querySelector<SVGSVGElement>("svg");
  const filterElement =
    document.querySelector<HTMLInputElement>("#node-filter");
  const forceElement =
    document.querySelector<HTMLInputElement>("#forces-toggle");
  const summaryElement = document.querySelector<HTMLElement>("#filter-summary");
  const shapeElements = Array.from(
    document.querySelectorAll<HTMLInputElement>('input[name="node-shape"]'),
  );

  if (
    !svgElement ||
    !filterElement ||
    !forceElement ||
    !summaryElement ||
    shapeElements.length < 2
  ) {
    throw new Error("The webview page is missing required graph controls.");
  }

  const nodeFilter = filterElement;
  const filterSummary = summaryElement;
  const svg = select<SVGSVGElement, unknown>(svgElement);
  const width = Number(svg.attr("width"));
  const height = Number(svg.attr("height"));
  const colors = scaleOrdinal<number, string>(schemeCategory10);
  let shape: NodeShape = "box";
  let forcesEnabled = forceElement.checked;

  sortAndIndexLinks(graph.links);
  svg
    .append("defs")
    .append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "-0 -5 10 10")
    .attr("refX", 13)
    .attr("refY", 0)
    .attr("orient", "auto")
    .attr("markerWidth", 13)
    .attr("markerHeight", 13)
    .attr("overflow", "visible")
    .append("path")
    .attr("d", "M 0,-5 L 10,0 L 0,5")
    .attr("fill", "#999")
    .style("stroke", "none");

  const linkForce = forceLink<GraphNode, GraphLink>()
    .id((node) => node.id)
    .distance(500)
    .strength(0.5);
  const simulation = forceSimulation<GraphNode>()
    .force("link", linkForce)
    .force("charge", forceManyBody())
    .force("center", forceCenter(width / 2, height / 2));

  const linkSelection: Selection<
    SVGPathElement,
    GraphLink,
    SVGSVGElement,
    unknown
  > = svg
    .selectAll<SVGPathElement, GraphLink>(".link")
    .data(graph.links)
    .enter()
    .append("path")
    .attr("class", "link")
    .attr("marker-end", "url(#arrowhead)");
  linkSelection.append("title").text((link) => link.name);

  const invisiblePathSelection: Selection<
    SVGPathElement,
    GraphLink,
    SVGSVGElement,
    unknown
  > = svg
    .selectAll<SVGPathElement, GraphLink>(".pathInvis")
    .data(graph.links)
    .enter()
    .append("path")
    .attr(
      "id",
      (link) =>
        `invis_${endpointId(link.source)}-${link.linkindex}-${endpointId(link.target)}`,
    )
    .attr("class", "pathInvis");

  const labelSelection: Selection<
    SVGTextElement,
    GraphLink,
    SVGSVGElement,
    unknown
  > = svg
    .selectAll<SVGTextElement, GraphLink>(".pathLabel")
    .data(graph.links)
    .enter()
    .append("text")
    .attr("class", "pathLabel")
    .attr("text-anchor", "middle");
  labelSelection
    .append("textPath")
    .attr("startOffset", "50%")
    .attr(
      "href",
      (link) =>
        `#invis_${endpointId(link.source)}-${link.linkindex}-${endpointId(link.target)}`,
    )
    .style("fill", "#ccc")
    .style("font-size", 10)
    .text((link) => link.name);

  const nodeSelection: Selection<
    SVGGElement,
    GraphNode,
    SVGSVGElement,
    unknown
  > = svg
    .selectAll<SVGGElement, GraphNode>(".node")
    .data(graph.nodes)
    .enter()
    .append("g")
    .attr("class", "node")
    .call(
      drag<SVGGElement, GraphNode>()
        .on("start", (event, node) => {
          if (forcesEnabled && !event.active) {
            simulation.alphaTarget(0.02).restart();
          }
          node.fx = node.x;
          node.fy = node.y;
        })
        .on("drag", (event, node) => {
          node.fx = event.x;
          node.fy = event.y;
          if (!forcesEnabled) {
            node.x = event.x;
            node.y = event.y;
            ticked();
          }
        }),
    );

  nodeSelection.append("title").text((node) => String(node.id));
  nodeSelection.append("text").text((node) => `${node.name}:${node.text}`);
  simulation.nodes(graph.nodes).on("tick", ticked);
  linkForce.links(graph.links);

  for (const shapeElement of shapeElements) {
    shapeElement.addEventListener("change", renderNodeShape);
  }
  nodeFilter.addEventListener("input", applyNodeFilter);
  forceElement.addEventListener("change", () => {
    forcesEnabled = forceElement.checked;
    if (forcesEnabled) {
      simulation.alpha(1).restart();
    } else {
      simulation.stop();
    }
  });

  renderNodeShape();
  applyNodeFilter();

  /** Update graph marks when the simulation advances or a node is dragged. */
  function ticked(): void {
    linkSelection.attr("d", (link) => bezierPath(true, link, shape));
    invisiblePathSelection.attr("d", (link) => {
      const source = endpointNode(link.source);
      const target = endpointNode(link.target);
      return bezierPath(source.x < target.x, link, shape);
    });
    nodeSelection.attr(
      "transform",
      (node) => `translate(${node.x}, ${node.y})`,
    );
  }

  /** Apply the selected shape and update label placement and link boundaries. */
  function renderNodeShape(): void {
    const selectedShape = shapeElements.find(
      (element) => element.checked,
    )?.value;
    if (selectedShape !== "box" && selectedShape !== "dot") {
      throw new Error("A valid node shape must be selected.");
    }
    shape = selectedShape;
    nodeSelection.selectAll(".node-shape").remove();

    if (shape === "box") {
      nodeSelection
        .insert("rect", "title")
        .attr("class", "node-shape")
        .attr("x", -NODE_WIDTH / 2)
        .attr("y", -NODE_HEIGHT / 2)
        .attr("width", NODE_WIDTH)
        .attr("height", NODE_HEIGHT)
        .attr("rx", 4)
        .style("fill", (_node, index) => colors(index));
    } else {
      nodeSelection
        .insert("circle", "title")
        .attr("class", "node-shape")
        .attr("r", NODE_DOT_RADIUS)
        .style("fill", (_node, index) => colors(index));
    }

    nodeSelection
      .select("text")
      .attr("x", shape === "box" ? 0 : NODE_DOT_RADIUS + 4)
      .attr("dy", shape === "box" ? 4 : -3)
      .attr("text-anchor", shape === "box" ? "middle" : "start");
    ticked();
  }

  /** Filter nodes, links, and labels, then announce the visible node count. */
  function applyNodeFilter(): void {
    const visibleIds = getVisibleNodeIds(graph.nodes, nodeFilter.value);
    nodeSelection.style("display", (node) =>
      visibleIds.has(node.id) ? null : "none",
    );

    /** Return whether both link endpoints are present in the filtered graph. */
    function linkIsVisible(link: GraphLink): boolean {
      return (
        visibleIds.has(endpointId(link.source)) &&
        visibleIds.has(endpointId(link.target))
      );
    }

    linkSelection.style("display", (link) =>
      linkIsVisible(link) ? null : "none",
    );
    invisiblePathSelection.style("display", (link) =>
      linkIsVisible(link) ? null : "none",
    );
    labelSelection.style("display", (link) =>
      linkIsVisible(link) ? null : "none",
    );
    filterSummary.textContent = `${visibleIds.size} of ${graph.nodes.length} nodes shown`;
  }
}
