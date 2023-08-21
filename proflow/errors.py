import json
from data_helpers.encoders import AdvancedJsonEncoder


class Run_Process_Error(Exception):
    def __init__(self, process: 'Process', error: Exception, state, args, kwargs):  # noqa F821

        process_id = process.comment or getattr(process.func, '__name__', 'Unknown')
        self.message = f'Failed to run "{process_id}"'
        self.error = error
        self.state = state
        self.process = process
        # self.args = args
        self.args_str = json.dumps(args, indent=4, cls=AdvancedJsonEncoder)
        # self.kwargs = kwargs
        self.kwargs_str = json.dumps(kwargs, indent=4, cls=AdvancedJsonEncoder)

    def __str__(self):
        # state_str = str(self.state)
        # state_print = state_str[0:100] + '...' + \
        #     state_str[:-100] if len(state_str) > 200 else state_str
        return f"""{self.message}
---------- Python Error ----------

{str(self.error)}

------------ Inputs ------------

args
----
{self.args_str}

kwargs:
-------
{self.kwargs_str}

        """
        # TODO: Find better way of showing state in error
        #  state:
        #  \n{state_print}
