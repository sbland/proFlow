from functools import partial, reduce
from proflow.parameters import Parameters_Shape
from proflow.external_state import External_State_Shape
from proflow.config import Config_Shape
from typing import Callable, List, NamedTuple
from .ProcessRunner import Process, run_process


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
        run_process_loaded = partial(run_process, config=self.config,
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
