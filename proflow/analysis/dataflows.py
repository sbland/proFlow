"""Compatibility imports for the canvas-based dataflow renderer.

Use :mod:`proflow.analysis.canvas` for new canvas rendering code.
"""

from proflow.analysis.canvas import (
    bezier_curve_canvas,
    link_processes_to_state,
    render_process_state_network,
    t_wrap,
)
from proflow.analysis.network.process_state import (
    ProcessStateNetwork,
    get_all_unique_inputs,
    get_inputs_map,
    get_links,
    processes_to_state_network,
)

__all__ = [
    "ProcessStateNetwork",
    "bezier_curve_canvas",
    "get_all_unique_inputs",
    "get_inputs_map",
    "get_links",
    "link_processes_to_state",
    "processes_to_state_network",
    "render_process_state_network",
    "t_wrap",
]
