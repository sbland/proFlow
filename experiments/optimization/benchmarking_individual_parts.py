"""Using CProfile to find bottlenecks."""
# %%
from proflow.helpers import rsetattr
from proflow.Objects.Interface import I
from proflow.Objects.Process import Process
from pstats import SortKey
from timeit import repeat
import pstats
import cProfile
from vendor.helpers.list_helpers import flatten_list
from proflow.ProcessRunnerCls import ProcessRunner
from proflow.tests.mocks import Mock_Model_State_Shape, Mock_Config_Shape, Mock_External_State_Shape, Mock_Nested_State
# from proflow.process_ins_and_outs import map_result_to_state
from proflow.process_state_modifiers import map_result_to_state_fn

# %%
def map_result_to_state(
    prev_state,
    output_map,
    result,
):
    # output_map(prev_state, result)
    # for o in output_map(result):
    #     rsetattr(prev_state, o.as_, o.from_)
    for from_, as_ in output_map(result):
        rsetattr(prev_state, as_, from_)
    return prev_state

prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)


def run_model_mutative():
    for i in range(100000):
        new_val = {'out': i}
        # new_state = map_result_to_state(prev_state, lambda prev_state, result: (
        #     rsetattr(prev_state, 'nested.na', result['out']),
        # ), new_val)
        new_state = map_result_to_state(prev_state, lambda result: [
            (result['out'], 'nested.na')
            # I(result['out'], as_='nested.na'),
        ], new_val)


run_model_mutative()

# %%
timetorun = min(repeat(lambda: run_model_mutative(), number=10, repeat=3))
timetorun
# 1.94 or 1.28


# %%


profile_output_file = 'experiments/optimization/benchmarking_individual_stats'
cProfile.run('run_model_mutative()', profile_output_file)

# %%
p = pstats.Stats(profile_output_file)
p.strip_dirs().sort_stats(SortKey.TIME).print_stats(30)#.print_callers(.5)

# %%
p = pstats.Stats(profile_output_file)
p.strip_dirs().sort_stats(SortKey.TIME).print_callees(30)#.print_callers(.5)


# %%


def run_model_non_mutative():
    for i in range(100000):
        prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
        new_val = i

        new_state = map_result_to_state_fn(prev_state, [
            I('out', as_='nested.na'),
        ], {'out': new_val})

run_model_non_mutative()

# %%
timetorun = min(repeat(lambda: run_model_non_mutative(), number=10, repeat=3))
timetorun
# 6.09214


# %%


# profile_output_file = 'experiments/optimization/benchmarking_individual_stats'
# cProfile.run('run_model_non_mutative()', profile_output_file)

# # %%
# p = pstats.Stats(profile_output_file)
# p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(30)#.print_callers(.5)

# # %%
# p = pstats.Stats(profile_output_file)
# p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_callees(30)#.print_callers(.5)

