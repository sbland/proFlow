import { IEdgeFull } from "./edges";
import { INode, TNodeId } from "./nodes";

export function arcPath(
  mLinkNum: { [k: string]: number },
  leftHand: boolean,
  d: IEdgeFull,
  nodes: { [k: TNodeId]: INode }
) {
  // var isOddLink = d.linkindex % 2 === 0;.
  // TODO: check why we already have node linked to edge data
  // const source = nodes[d.source];
  // const target = nodes[d.target];
  const source = d.source;
  const target = d.target;
  if (!source || !target) {
    console.info(nodes);
    console.info(d);
    throw Error("Node not found!");
  }
  var x1 = leftHand ? source.x : target.x,
    y1 = leftHand ? source.y : target.y,
    x2 = leftHand ? target.x : source.x,
    y2 = leftHand ? target.y : source.y,
    dx = x2 - x1,
    dy = y2 - y1,
    dr = Math.sqrt(dx * dx + dy * dy);

  var sweep = leftHand ? 0 : 1;
  var xRotation = 0;
  var largeArc = 0;

  var dx = target.x - source.x,
    dy = target.y - source.y,
    dr = Math.sqrt(dx * dx + dy * dy);

  // get the total link numbers between source and target node
  var siblingCount =
    mLinkNum[source.id + "," + target.id] ||
    mLinkNum[target.id + "," + source.id];
  if (siblingCount > 1) {
    // if there are multiple links between these two nodes, we need generate different dr for each path
    dr = dr / (1 + (1 / siblingCount) * (d.linkindex - 1 - sweep));
  }

  return (
    "M" +
    x1 +
    "," +
    y1 +
    "A" +
    dr +
    ", " +
    dr +
    " " +
    xRotation +
    ", " +
    largeArc +
    ", " +
    sweep +
    " " +
    x2 +
    "," +
    y2
  );
}
