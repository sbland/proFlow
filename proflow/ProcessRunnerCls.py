from datetime import datetime
from functools import partial, reduce
from proflow.process_ins_and_outs import get_inputs_from_process, map_result_to_state
from typing import Callable, List, NamedTuple

from .parameters import Parameters_Shape
from .external_state import External_State_Shape
from .config import Config_Shape
from .ProcessRunner import Process
from .errors import Run_Process_Error


class ProcessRunner():
    """A class for initializing the process runner"""

    def __init__(self,
                 config_in: Config_Shape = Config_Shape(),
                 external_state_in: External_State_Shape = External_State_Shape(),
                 parameters_in: Parameters_Shape = Parameters_Shape(),
                 DEBUG_MODE: bool = False):
        self.config = config_in
        self.parameters = parameters_in
        self.external_state = external_state_in
        self.DEBUG_MODE = DEBUG_MODE
        self.time_logs = []
        self.debug_time_logs = []

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
        run_process_loaded = partial(self.run_process, config=self.config,
                                     parameters=self.parameters,
                                     external_state=self.external_state,
                                     DEBUG_MODE=self.DEBUG_MODE)
        new_state = reduce(run_process_loaded, processes, initial_state)
        return new_state

    def initialize_processes(
        self,
        processes: List[Process]
    ) -> Callable[[NamedTuple], NamedTuple]:
        """HOC component to assign processes to the run_processes function
        which can then be ran later with the state"""
        return partial(self.run_processes, processes)

    def run_process(
        self,
        prev_state: NamedTuple,  # Can be state or parameter
        process: Process,
        config: Config_Shape,
        parameters: Parameters_Shape,
        external_state: External_State_Shape,
        DEBUG_MODE: bool = False,
    ) -> NamedTuple:
        """Run a single process and output the updated state.
            The process object contains the function along with all the input
            and output targets.


            note: args from process are not garuanteed to be in the correct order

        Parameters
        ----------
        prev_state : NamedTuple
            Model state prior to this process being ran
        config : Config_Shape
            Model configuration
        parameters : Parameters_Shape
            Model derived parameters
        external_state : External_State_Shape
            External data
        DEBUG_MODE : bool, optional
            Debug processes when True, by default False

        Returns
        -------
        Model State
            Model State after process

        Raises
        ------
        Run_Process_Error
            Catches error that occur when running the process
        """
        if not process.gate:
            return prev_state
        try:
            process_id = process.comment or getattr(process.func, '__name__', 'Unknown')
            if DEBUG_MODE:
                start_time_input_setup = datetime.now()

            args, kwargs = get_inputs_from_process(
                process,
                prev_state,
                config,
                parameters,
                external_state,
            )

            if DEBUG_MODE:
                end_time_input_setup = datetime.now()
                time_diff_input_setup = (end_time_input_setup - start_time_input_setup)
                execution_time_input_setup = time_diff_input_setup.total_seconds() * 1000

            # RUN PROCESS FUNC
            result = None
            if DEBUG_MODE:
                # Log time taken for process
                start_time = datetime.now()
                result = process.func(*args, **kwargs)
                end_time = datetime.now()
                time_diff = (end_time - start_time)
                execution_time = time_diff.total_seconds() * 1000

                self.time_logs.append((process_id, execution_time))
            else:
                result = process.func(*args, **kwargs)

            if DEBUG_MODE:
                start_time_output_setup = datetime.now()

            output_state = map_result_to_state(prev_state, process.state_outputs, result)

            if DEBUG_MODE:
                end_time_output_setup = datetime.now()
                time_diff_output_setup = (end_time_output_setup - start_time_output_setup)
                execution_time_output_setup = time_diff_output_setup.total_seconds() * 1000

            if DEBUG_MODE:
                self.debug_time_logs.append({
                    "id": process_id,
                    "input_time": execution_time_input_setup,
                    "output_time": execution_time_output_setup,
                })

            return output_state

        except Exception as e:
            raise Run_Process_Error(process, e, prev_state) from e

    def reset_logs(self):
        self.time_logs = []
        self.debug_time_logs = []
