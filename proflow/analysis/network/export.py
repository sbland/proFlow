import json
from dataclasses import asdict

import networkx as nx

from proflow.analysis.network.extract_nodes_and_edges import Edge, Node


def asjson(nodes: list[Node], edges: list[Edge], output_file: str):
    G = nx.MultiDiGraph()
    for n in nodes:
        G.add_node(n.index, **asdict(n))

    edge_data = [(e.target, e.source, asdict(e)) for e in edges if e.target != -1]
    G.add_edges_from(edge_data)

    # %%
    json_graph_data = nx.json_graph.node_link_data(
        G, {"source": "source", "target": "target", "name": "id", "key": "key", "link": "links"}
    )

    with open(output_file, "w") as output:
        json.dump(json_graph_data, output)
    return json_graph_data
