"""Using CProfile to find bottlenecks."""

from proflow.Objects.Interface import I
from proflow.Objects.Process import Process
from pstats import SortKey
from timeit import repeat
import pstats
import cProfile
from vendor.helpers.list_helpers import flatten_list
from proflow.ProcessRunnerCls import ProcessRunner
from proflow.tests.mocks import Mock_Model_State_Shape, Mock_Config_Shape, Mock_External_State_Shape
# %%
config = Mock_Config_Shape(1.1, 2.2)

process_runner = ProcessRunner(config, DEBUG_MODE=True)

# %%
process_runner.external_state = Mock_External_State_Shape()

# %%
# == SETUP INITIAL STATE
initial_state = Mock_Model_State_Shape(1, 2)
initial_state.matrix = [[i * j for i in range(100)] for j in range(100)]
# %%


DEMO_PROCESSES = [
    Process(
        func=lambda x, y, z: x + y + z,
        comment="Demo process a",
        config_inputs=lambda config: [
            I(config.foo, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.nested_lst_obj[0].na, as_='y'),
            I(state.matrix[0][0], as_='z')
        ],
        state_outputs=[
            I('_result', as_='nested_lst_obj.0.na'),
        ]
    )
for i in range(10000)]

# %%
final_state = process_runner.run_processes(
        flatten_list(DEMO_PROCESSES),
        initial_state,
    )
# %%

def run_model():
    final_state = process_runner.run_processes(
        flatten_list(DEMO_PROCESSES),
        initial_state,
    )

# %%
timetorun = min(repeat(lambda: run_model(), number=10, repeat=3))
timetorun

# %%


profile_output_file = 'experiments/optimization/run_model_full_stats'
cProfile.run('run_model()', profile_output_file)

# %%
p = pstats.Stats(profile_output_file)
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(30)#.print_callers(.5)

# %%
with open('output_profile_stats.txt', 'w') as f:
    p = pstats.Stats(profile_output_file, stream=f)
    r = p.sort_stats(SortKey.TIME, SortKey.CUMULATIVE).print_stats(.5).print_callers(10)
# %%
with open('output_profile_statsb.txt', 'w') as f:
    p = pstats.Stats(profile_output_file, stream=f)
    r = p.sort_stats(SortKey.CUMULATIVE, SortKey.TIME).print_stats(.5).print_callees(10)
