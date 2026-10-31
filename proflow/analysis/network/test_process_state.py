from proflow.objects.interface import I
from proflow.objects.process import Process

from .process_state import processes_to_state_network


def test_processes_to_state_network():
    process = Process(
        func=lambda value: value,
        comment="copy state",
        state_inputs=[I("state.before", as_="value")],
        state_outputs=[I("_result", as_="state.after")],
    )

    network = processes_to_state_network([process])

    assert set(network.state_keys) == {"state.before", "state.after"}
    assert network.input_links == [[network.state_keys.index("state.before")]]
    assert network.output_links == [[network.state_keys.index("state.after")]]


def test_processes_to_state_network_filters_state_keys():
    process = Process(
        func=lambda value: value,
        state_inputs=[I("state.before", as_="value")],
        state_outputs=[I("_result", as_="state.after")],
    )

    network = processes_to_state_network([process], "before")

    assert network.state_keys == ["state.before"]
    assert network.input_links == [[0]]
    assert network.output_links == [[]]
