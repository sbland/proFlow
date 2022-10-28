import { TNodeId } from "./nodes";

export type TEdgeId = number;

export interface IEdgeRaw {
  linkindex: number;
}

export interface IEdge extends IEdgeRaw {
  source: TNodeId;
  target: TNodeId;
  name: string;
  id: TEdgeId;
  key: number;
}
