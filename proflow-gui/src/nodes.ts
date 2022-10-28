export type TNodeId = number;

export interface INode {
  index: number;
  id: TNodeId;
  x: number;
  y: number;
  name: string;
  text: string;
}