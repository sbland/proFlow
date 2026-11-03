# proFlow

proFlow is a Python library for running an ordered sequence of processes against
an application state. Each process is a function whose inputs are selected from
state (and optionally configuration, parameters, or external data) and whose
result is mapped back to state.

Processes should be pure functions: they compute and return values rather than
modifying the input state directly. This makes process behavior easier to test
and reason about.

## Features

- Run an ordered list of reusable process definitions.
- Map process inputs and outputs using state attributes and dotted paths.
- Supply configuration, parameters, external state, and additional inputs.
- Optionally update supported state objects without mutating the original.
- Inspect process dependencies and visualize data flows with the analysis tools.

## Installation

proFlow requires Python 3.14 or newer and is available on PyPI:

```shell
python -m pip install proflow
```

## Quick start

Define a state, a function, and a `Process` that maps the state value into the
function and maps its result back to the state. `IMMUTABLE_MODE=True` makes the
runner return an updated dataclass without modifying the original.

```python
from dataclasses import dataclass

from proflow.objects.interface import I
from proflow.objects.process import Process
from proflow.process_runner import ProcessRunner


@dataclass(frozen=True)
class State:
    count: int = 0


def increment(count: int) -> int:
    return count + 1


increment_process = Process(
    func=increment,
    state_inputs=lambda state: [I(state.count, as_="count")],
    state_outputs=lambda result: [(result, "count")],
)

runner = ProcessRunner(IMMUTABLE_MODE=True)
initial_state = State()
result = runner.run_processes([increment_process], initial_state=initial_state)

assert result.count == 1
assert initial_state.count == 0
```

## How it works

`ProcessRunner` runs processes in order, passing the state returned by one
process to the next. A `Process` describes the function to call and how its
inputs and outputs connect to the surrounding data:

- **Inputs** are provided with callables such as `state_inputs`. Each returns
  `I(value, as_="argument_name")` entries; the `as_` value becomes the
  corresponding keyword argument to the function.
- **Outputs** are provided by `state_outputs`. The callable receives the
  function result and returns `(value, "target.path")` pairs to write into
  state.
- **Other input sources** include `config_inputs`, `parameters_inputs`,
  `external_state_inputs`, and `additional_inputs`.
- **Process options** include `gate` to skip a process, `comment` and `group`
  for descriptions, and `args` for additional positional arguments.

By default, output mapping updates state in place. Set
`ProcessRunner(IMMUTABLE_MODE=True)` to use the non-mutating update path for
supported dataclasses, dictionaries, and lists.

## API and examples

The main entry points are:

- [`Process`](./proflow/objects/process.py) defines a function and its input and
  output mappings.
- [`I`](./proflow/objects/interface.py) describes an input value and optional
  function argument name.
- [`ProcessRunner`](./proflow/process_runner.py) configures and runs processes.
- [`proflow/analysis`](./proflow/analysis) contains process and data-flow
  inspection tools.
- [`proflow/tests/demodata.py`](./proflow/tests/demodata.py) contains a small
  example process sequence; the [experiments](./experiments) directory has
  analysis and visualization examples.

## Development

Clone the repository, install the project and development dependencies, then
run the tests and style checks:

```shell
uv sync --all-groups
source .venv/bin/activate
python -m pytest
ruff check .
ruff format . --check
```

## License

proFlow is distributed under the terms of the [MIT License](./LICENSE).
