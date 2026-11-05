# Process analysis and network diagrams

The `proflow.analysis` package separates building process networks from
rendering diagrams:

- `proflow.analysis.network` produces process nodes and state-dependency
  edges. The `process_state` module also builds the state/link data used by the
  canvas diagram. The network can be exported as NetworkX node-link JSON.
- `proflow.analysis.canvas` draws process and state nodes directly onto an
  `ipycanvas` canvas.

Both workflows use each process's `state_inputs` and `state_outputs`. Config,
parameter, external-state, and additional inputs are not included in the
network links.

## Define processes

The examples below use `I(from_, as_)` to describe state mappings. For an
input, `from_` is the state key read by the process. For an output, `as_` is
the state key written by the process.

```python
from proflow.objects import I, Process


def add_today_and_hour(today, hour):
    return today + hour


processes = [
    Process(
        func=add_today_and_hour,
        comment="Calculate tomorrow",
        state_inputs=[
            I("state.info.today", as_="today"),
            I("state.info.hour", as_="hour"),
        ],
        state_outputs=[I("_result", as_="state.info.tomorrow")],
    ),
    Process(
        func=lambda tomorrow: tomorrow * 2,
        comment="Calculate the next value",
        state_inputs=[I("state.info.tomorrow", as_="tomorrow")],
        state_outputs=[I("_result", as_="state.info.next")],
    ),
]
```

Keep the process order meaningful: the network workflow looks for the most
recent earlier process that outputs each input state key.

## Draw processes and state with a canvas

`link_processes_to_state` draws process rectangles, state rectangles, and
curved links onto a canvas-like object. State inputs are shown with blue links;
state outputs use red links. The function returns the canvas. Canvas rendering
is a separate workflow from building/exporting the process network.

```python
from ipycanvas import Canvas
from proflow.analysis.canvas import render_process_state_network
from proflow.analysis.network.process_state import processes_to_state_network

network = processes_to_state_network(processes)
canvas = Canvas(width=900, height=500)
render_process_state_network(canvas, processes, network, seperation=300)
```

For convenience, `link_processes_to_state(canvas, processes, ...)` combines
those two steps. Existing imports from `proflow.analysis.dataflows` continue
to work; new code should import network construction from
`proflow.analysis.network.process_state` and rendering from
`proflow.analysis.canvas`.

The optional arguments control the layout and labels:

- `seperation`: horizontal gap between process and state columns.
- `process_node_width`, `process_node_height`: process rectangle dimensions.
- `state_node_width`, `state_node_height`: state rectangle dimensions.
- `LP`, `TP`, `FONT_SIZE`: left/top padding and label font size.
- `filter_state_string` on `processes_to_state_network`: a regular-expression
  pattern used to select state keys; by default all state keys are included.
  A compiled regular expression can also be passed.

This helper expects an `ipycanvas`-compatible canvas. Display the resulting
canvas using the interface of the environment in which it is running, such as
a Jupyter notebook.

## Build nodes and edges

For applications that need graph data rather than an immediate canvas drawing,
use `processes_to_nodes_and_edges`:

```python
from proflow.analysis.network.extract_nodes_and_edges import (
    processes_to_nodes_and_edges,
)

nodes, edges = processes_to_nodes_and_edges(processes)
```

Each `Node` has an index matching its position in `processes`, the function
name, and the process comment. Each `Edge` represents one state input. Its
`name` is the state key, `source` is the consuming process index, and `target`
is the index of the most recent earlier process that wrote that key. A
`target` of `-1` means no earlier output for that state key was found.

## Export graph data as JSON

`asjson` converts the node and edge records into NetworkX node-link data and
writes that data to a JSON file:

```python
from proflow.analysis.network.export import asjson

graph_data = asjson(nodes, edges, "process-network.json")
```

The exported graph uses producer-to-consumer direction for its links, even
though an `Edge` record's `source` field identifies the consumer and its
`target` field identifies the producer. Edges without a preceding producer
(`target == -1`) are omitted from the exported graph. The function returns
the same node-link data it writes.

## Explore a network in the web view

The optional Flask web view displays the process network as an interactive
force-directed graph. Install Flask if needed, then run it from the project root:

```bash
python -m pip install flask
python -m proflow.analysis.webview.run_app
```

Open the printed local URL and use the **Search nodes** field to match node IDs,
function names, or process descriptions without regard to case. The graph hides
nonmatching nodes and links that connect to hidden nodes; clearing the search
restores the full network. Use **Enable forces** to pause or resume the
force-directed layout, and **Node shape** to switch between labeled boxes (the
default) and dots. Dragging nodes remains available while forces are paused.
Use the mouse wheel or a touch gesture to zoom, and drag empty canvas to pan.
The **Zoom in**, **Zoom out**, and **Reset** buttons provide equivalent controls;
reset returns to the original view. Zoom is bounded so the graph cannot become
arbitrarily small or large. Panning and zooming do not interfere with dragging
nodes.
In box mode, incoming links connect to the left edge and outgoing links leave
the right edge, with cubic Bézier curves that leave and meet the boxes
perpendicularly. Node labels remain visible in both modes.

### Develop the webview frontend

The frontend is a private Node ES-module package in
[`proflow_webview`](../../proflow_webview).
It uses TypeScript for strict type checking, Vite to build, Vitest for unit
tests, and Playwright for browser tests. The Python package serves the compiled
assets and provides graph data at `/data`; Node is needed only to develop and
build the frontend, not to run an installed Python package.

Use Node 22 or newer and install frontend dependencies from the repository root:

```bash
pnpm --dir proflow_webview install --frozen-lockfile
```

For frontend development, start the Flask server in one terminal and Vite in
another. Vite proxies `/data` to the Flask server on port 8000:

```bash
uv sync --locked --group web
uv run --locked python -m proflow.analysis.webview.run_app
pnpm --dir proflow_webview dev
```

Run the frontend checks and build compiled assets for the Flask server:

```bash
pnpm --dir proflow_webview typecheck
pnpm --dir proflow_webview lint
pnpm --dir proflow_webview format:check
pnpm --dir proflow_webview test
pnpm --dir proflow_webview build
```

The build output is stored in
`proflow/analysis/webview/static/force/frontend-dist` and included in Python
source and binary distributions. The Playwright suite starts the Flask server
automatically; install Chromium first with
`pnpm --dir proflow_webview playwright:install`, then run
`pnpm --dir proflow_webview test:e2e`. Python route tests are included in the
project pytest suite.

## Dependencies

The canvas workflow requires `ipycanvas`. JSON export requires `networkx`.
These are not declared as core project dependencies, so install the package
needed for the workflow you use, for example:

```bash
python -m pip install ipycanvas networkx
```
