from proflow.tests.demodata import DEMO_PROCESSES
from .extract_nodes_and_edges import get_process_link_data, get_successive_edges, \
    process_to_node, processes_to_nodes, Node_Link_Data, Edge, Node, processes_to_nodes_and_edges


DEMO_STATE_INPUTS = [
    Node_Link_Data(node_index=0, state_key='state.info.today'),
    Node_Link_Data(node_index=0, state_key='state.info.hour'),
    Node_Link_Data(node_index=1, state_key='state.info.tomorrow'),
    Node_Link_Data(node_index=2, state_key='state.info.tomorrow'),
    Node_Link_Data(node_index=3, state_key='state.info.today'),
]

DEMO_STATE_OUTPUTS = [
    Node_Link_Data(node_index=0, state_key='state.info.tomorrow'),
    Node_Link_Data(node_index=1, state_key='state.info.today'),
    Node_Link_Data(node_index=2, state_key='state.info.today'),
    Node_Link_Data(node_index=3, state_key='state.info.tomorrow'),
]

DEMO_NODES = [
    Node(index=0, x=0, y=0, name='<lambda>', text='Demo process a'),
    Node(index=1, x=1, y=0, name='<lambda>', text='Demo process b'),
    Node(index=2, x=2, y=0, name='<lambda>', text='Demo process c'),
    Node(index=3, x=3, y=0, name='<lambda>', text='Demo process d'),
]

DEMO_EDGES = [
    Edge(source=0, target=-1, name='state.info.today'),
    Edge(source=0, target=-1, name='state.info.hour'),
    Edge(source=1, target=0, name='state.info.tomorrow'),
    Edge(source=2, target=0, name='state.info.tomorrow'),
    Edge(source=3, target=2, name='state.info.today'),
]


def test_get_process_link_data():
    """Test get_process_link_data returns correct data."""
    out = get_process_link_data(DEMO_PROCESSES)
    assert out == (DEMO_STATE_INPUTS, DEMO_STATE_OUTPUTS)


def test_get_successive_edges():
    """Test get_successive_edges returns correct data."""
    out = get_successive_edges(
        state_inputs=DEMO_STATE_INPUTS,
        state_outputs=DEMO_STATE_OUTPUTS,
    )
    assert out == DEMO_EDGES


def test_process_to_node():
    """Test process_to_node returns correct data."""
    out = process_to_node(DEMO_PROCESSES[0], 0)
    assert out == DEMO_NODES[0]


def test_processes_to_nodes():
    """Test processes_to_nodes returns correct data."""
    out = processes_to_nodes(DEMO_PROCESSES)
    assert out == DEMO_NODES


def test_processes_to_nodes_and_edges():
    """Test processes_to_nodes_and_edges returns correct data."""
    out = processes_to_nodes_and_edges(DEMO_PROCESSES)
    (
        [
            Node(index=0, x=0, y=0, name='<lambda>', text='Demo process a'),
            Node(index=1, x=1, y=0, name='<lambda>', text='Demo process b'),
            Node(index=2, x=2, y=0, name='<lambda>', text='Demo process c'),
            Node(index=3, x=3, y=0, name='<lambda>', text='Demo process d')
        ],
        [
            Edge(source=0, target=-1, name='info.today'),
            Edge(source=0, target=-1, name='info.hour'),
            Edge(source=1, target=-1, name='info.tomorrow'),
            Edge(source=2, target=-1, name='info.tomorrow'),
            Edge(source=3, target=-1, name='info.today')
        ]
    )
    assert out == (DEMO_NODES, DEMO_EDGES)
