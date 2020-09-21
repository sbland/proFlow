import sys
import os
module_path = os.path.abspath(os.path.join('../../'))
if module_path not in sys.path:
    sys.path.append(module_path)



# %%
import json
from dataclasses import asdict
import matplotlib.pyplot as plt
import networkx as nx
from proflow.analysis.horizontal_flow_analysis.extract_nodes_and_edges import Edge, Node


DEMO_NODES = [
    Node(index=0, x=0, y=0, name='<lambda>', text='Demo process a'),
    Node(index=1, x=1, y=0, name='<lambda>', text='Demo process b'),
    Node(index=2, x=2, y=0, name='<lambda>', text='Demo process c'),
    Node(index=3, x=3, y=0, name='<lambda>', text='Demo process d'),
    Node(index=4, x=3, y=0, name='<lambda>', text='Demo process e'),
    Node(index=5, x=3, y=0, name='<lambda>', text='Demo process f'),
]

DEMO_EDGES = [
    Edge(source=0, target=-1, name='info.today'),
    Edge(source=0, target=-1, name='info.hour'),
    Edge(source=1, target=0, name='info.tomorrow'),
    Edge(source=2, target=0, name='info.tomorrow'),
    Edge(source=3, target=2, name='info.today'),
    Edge(source=4, target=2, name='info.other'),
    Edge(source=4, target=1, name='info.other'),
    Edge(source=5, target=4, name='info.other'),
]

G = nx.MultiDiGraph()
for n in DEMO_NODES:
    G.add_node(n.index, **asdict(n))

edge_data = [(e.target, e.source, asdict(e)) for e in DEMO_EDGES if e.target != -1]
G.add_edges_from(edge_data)


nx.draw(G, with_labels=True)
plt.show()

# %%
json_graph_data = nx.json_graph.node_link_data(
    G,
    dict(source='source', target='target', name='id',
     key='key', link='links')
)

json.dump(json_graph_data, open("static/force/force.json", "w"))
