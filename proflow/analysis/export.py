"""Export process analysis results to the force webview JSON format."""

from dataclasses import asdict

from proflow.analysis.network.extract_nodes_and_edges import Edge, Node


def processes_to_json(
    nodes_and_edges: tuple[list[Node], list[Edge]],
) -> dict[str, object]:
    """Write process nodes and edges as force webview node-link JSON.

    The returned graph data is also written to ``output_file``. Unresolved
    edges, whose ``target`` is ``-1``, are omitted from the links.
    """
    nodes, edges = nodes_and_edges
    graph_data: dict[str, object] = {
        "directed": True,
        "multigraph": True,
        "graph": {},
        "nodes": [{**asdict(node), "id": node.index} for node in nodes],
        "links": [
            {
                "source": edge.target,
                "target": edge.source,
                "name": edge.name,
                "key": 0,
                "id": link_id,
            }
            for link_id, edge in enumerate(
                (edge for edge in edges if edge.target != -1),
                start=1,
            )
        ],
    }

    return graph_data
