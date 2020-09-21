from dataclasses import dataclass
from collections import namedtuple
from typing import List, Tuple

from proflow.Objects import Process


@dataclass
class Edge:
    source: int
    target: int
    name: str


@dataclass
class Node:
    index: int
    x: float
    y: float
    name: str
    text: str

@dataclass
class Node_Link_Data:
    node_index: int
    state_key: str


def get_process_link_data(
    processes: List[Process],
) -> Tuple[List[Node_Link_Data]]:
    state_inputs_link_data = [
        Node_Link_Data(i, inp.from_) for i, p in enumerate(processes) for inp in p.state_inputs
    ]
    state_outputs_link_data = [
        Node_Link_Data(i, outp.as_) for i, p in enumerate(processes) for outp in p.state_outputs
    ]
    return state_inputs_link_data, state_outputs_link_data


def get_successive_edges(
    state_inputs: List[Node_Link_Data],
    state_outputs: List[Node_Link_Data],
) -> List[Edge]:
    """Get a link from 1 process to the next using its modification to the state."""
    links = []
    for i, s_input in enumerate(state_inputs):
        # get state outputs before this node
        lookup_state_outputs = list(state_outputs[:i])[::-1]
        try:
            # Find the most recent node to output this input
            target_output_index = next(
                oput.node_index for oput in lookup_state_outputs if oput.state_key == s_input.state_key)
        except:
            # If not found link is null
            target_output_index = -1
        # print(n)
        edge = Edge(source=s_input.node_index, target=target_output_index, name=s_input.state_key)
        links.append(edge)
    return links
# edges = get_successive_edges(state_inputs, state_outputs)


def process_to_node(p: Process, i: int) -> Node:
    return Node(
        index=i,
        x=i,
        y=0,
        name=p.func.__name__,
        text=p.comment,
    )


def processes_to_nodes(processes: List[Process]) -> List[Node]:
    nodes = [process_to_node(p, i) for i, p in enumerate(processes)]
    return nodes
