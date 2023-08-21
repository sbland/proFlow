from copy import deepcopy
from datetime import datetime
from functools import partial, reduce
from proflow.internal_state import Model_State_Shape
from proflow.TimeManager import TimeManager, TimeScale
from proflow.process_state_modifiers import map_result_to_state_fn
from proflow.process_ins_and_outs import get_inputs_from_process, map_result_to_state
from typing import Callable, List, NamedTuple

from .parameters import Parameters_Shape
from .external_state import External_State_Shape
from .config import Config_Shape
from .Objects.Process import Process, ProcessType
from .errors import Run_Process_Error


class ProcessRunner():
    """A class for initializing the process runner"""

    def __init__(self,
                 config_in: Config_Shape = Config_Shape(),
                 external_state_in: External_State_Shape = External_State_Shape(),
                 parameters_in: Parameters_Shape = Parameters_Shape(),
                 DEBUG_MODE: bool = False,
                 IMMUTABLE_MODE: bool = False,
                 row_per: TimeScale = TimeScale.HOUR,
                 ):
        self.config = config_in
        self.parameters = parameters_in
        self.external_state = external_state_in
        self.DEBUG_MODE = DEBUG_MODE
        self.IMMUTABLE_MODE = IMMUTABLE_MODE
        self.state_logs = [{}]
        self.time_logs = []
        self.debug_time_logs = []
        self.tm = TimeManager(row_per=row_per)

    def reset(self):
        self.state_logs = [{}]
        self.time_logs = []
        self.debug_time_logs = []
        self.tm = TimeManager(row_per=self.tm.row_per)

    # Define the process runner
    def run_processes(
        self,
        processes: List[Process] = None,
        initial_state: NamedTuple = None,  # initial state or parameters
    ) -> NamedTuple:
        """ Takes the initial state and a list of processes
        returns the new state as modified by the processes

        new state is the state after we have run all the processes
        the reduce function allows us to iterate through each function
        passing the state to the next
        """
        _initial_state = initial_state or self.current_state
        self.current_state = reduce(self.process_switcher, processes, _initial_state)
        return self.current_state

    def initialize_processes(
        self,
        processes: List[Process]
    ) -> Callable[[NamedTuple], NamedTuple]:
        """HOC component to assign processes to the run_processes function
        which can then be ran later with the state"""
        return partial(self.run_processes, processes)

    def process_switcher(
        self,
        prev_state: Model_State_Shape,
        process: Process,
        *args,
        **kwargs,
    ):
        """Ran for each process on state."""
        if process.ptype == ProcessType.STANDARD:
            if self.DEBUG_MODE:
                return self.run_process_debug(prev_state, process, *args, **kwargs)
            else:
                return self.run_process(prev_state, process, *args, **kwargs)
        if process.ptype == ProcessType.TIME:
            return self.run_process_time(prev_state, process, *args, **kwargs)
        if process.ptype == ProcessType.LOG:
            return self.run_process_log(prev_state, process, *args, **kwargs)

    def run_process_log(
        self,
        prev_state: NamedTuple,  # Can be state or parameter
        process: Process,
    ):
        row_index = self.tm.row_index
        if row_index >= len(self.state_logs):
            new_rows = [{} for i in range(row_index - len(self.state_logs) + 1)]
            self.state_logs += new_rows
        args, kwargs = get_inputs_from_process(
            process,
            prev_state,
            self.config,
            self.parameters,
            self.external_state,
            row_index,
        )

        self.state_logs[row_index] = {**self.state_logs[row_index], **kwargs}
        return prev_state

    def run_process_time(
        self,
        prev_state: NamedTuple,  # Can be state or parameter
        process: Process,
    ):
        process.func(tm=self.tm)
        return prev_state

    def run_process(
        self,
        prev_state: NamedTuple,  # Can be state or parameter
        process: Process,
    ):
        """Run a single process and output the updated state.
            The process object contains the function along with all the input
            and output targets.


            note: args from process are not guaranteed to be in the correct order

        Parameters
        ----------
        self
            Contains config, parameters and external state
            config : Config_Shape
                Model configuration
            parameters : Parameters_Shape
                Model derived parameters
            external_state : External_State_Shape
                External data
        prev_state : NamedTuple
            Model state prior to this process being ran
        process: Process
            The process to run

        Returns
        -------
        Model State
            Model State after process
        """
        config: Config_Shape = self.config
        parameters: Parameters_Shape = self.parameters
        external_state: External_State_Shape = self.external_state
        IMMUTABLE_MODE: bool = self.IMMUTABLE_MODE
        row_index: int = self.tm.row_index

        modified_state = deepcopy(prev_state) if IMMUTABLE_MODE else prev_state

        if not process.gate:
            return modified_state
        args, kwargs = get_inputs_from_process(
            process,
            modified_state,
            config,
            parameters,
            external_state,
            row_index,
        )

        # RUN PROCESS FUNC
        result = process.func(*args, **kwargs)

        output_state = map_result_to_state(modified_state, process.state_outputs, result) \
            if not process.format_output else \
            map_result_to_state_fn(modified_state, process.state_outputs, result)

        return output_state

    def run_process_debug(
        self,
        prev_state: NamedTuple,  # Can be state or parameter
        process: Process,
    ) -> NamedTuple:
        """Run a single process and output the updated state.
            The process object contains the function along with all the input
            and output targets.

            Debug mode:
                Logs the time intervals


            note: args from process are not guaranteed to be in the correct order

        Parameters
        ----------
        self
            Contains config, parameters and external state
            config : Config_Shape
                Model configuration
            parameters : Parameters_Shape
                Model derived parameters
            external_state : External_State_Shape
                External data
        prev_state : NamedTuple
            Model state prior to this process being ran
        process: Process
            The process to run

        Returns
        -------
        Model State
            Model State after process

        Raises
        ------
        Run_Process_Error
            Catches error that occur when running the process
        """
        config: Config_Shape = self.config
        parameters: Parameters_Shape = self.parameters
        external_state: External_State_Shape = self.external_state
        IMMUTABLE_MODE: bool = self.IMMUTABLE_MODE
        row_index: int = self.tm.row_index
        args, kwargs = None, None
        if not process.gate:
            return prev_state
        try:
            modified_state = deepcopy(prev_state) if IMMUTABLE_MODE else prev_state
            process_id = process.comment or getattr(process.func, '__name__', 'Unknown')
            start_time_input_setup = datetime.now()

            args, kwargs = get_inputs_from_process(
                process,
                modified_state,
                config,
                parameters,
                external_state,
                row_index,
            )

            end_time_input_setup = datetime.now()
            time_diff_input_setup = (end_time_input_setup - start_time_input_setup)
            execution_time_input_setup = time_diff_input_setup.total_seconds() * 1000

            # RUN PROCESS FUNC
            # Log time taken for process
            start_time = datetime.now()
            result = process.func(*args, **kwargs)
            end_time = datetime.now()
            time_diff = (end_time - start_time)
            execution_time = time_diff.total_seconds() * 1000

            self.time_logs.append((process_id, execution_time))

            start_time_output_setup = datetime.now()

            # TODO: This is expensive!
            output_state = map_result_to_state(modified_state, process.state_outputs, result) \
                if not process.format_output else \
                map_result_to_state_fn(modified_state, process.state_outputs, result)

            end_time_output_setup = datetime.now()
            time_diff_output_setup = (end_time_output_setup - start_time_output_setup)
            execution_time_output_setup = time_diff_output_setup.total_seconds() * 1000

            self.debug_time_logs.append({
                "id": process_id,
                "input_time": execution_time_input_setup,
                "output_time": execution_time_output_setup,
            })

            return output_state

        except Exception as e:
            raise Run_Process_Error(process, e, modified_state, args, kwargs) from e

    def reset_logs(self):
        self.time_logs = []
        self.debug_time_logs = []


def advance_time_step_process():
    """Helper Process to advance a time step."""
    def advance_time_step(tm: TimeManager):
        tm.advance_row()
    return Process(
        func=advance_time_step,
        ptype=ProcessType.TIME,
    )
