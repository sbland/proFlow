import json
from data_helpers.encoders import AdvancedJsonEncoder


class Run_Process_Error(Exception):
    def __init__(self, process: 'Process', error: Exception, state, args, kwargs):  # noqa F821

        process_id = process.comment or getattr(process.func, '__name__', 'Unknown')
        self.message = f'Failed to run "{process_id}"'
        self.error = error
        self.state = state
        self.process = process
        self.args_str = json.dumps(args, indent=4, cls=AdvancedJsonEncoder)
        self.kwargs_str = json.dumps(kwargs, indent=4, cls=AdvancedJsonEncoder)
        try:
            self.human = json.dumps(self.process.human(), indent=4, cls=AdvancedJsonEncoder)
        except Exception as e:
            self.human = f"""Could not parse process for error message!

            Error:
            {e}
            """

    def __str__(self):
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


------------- Code -------------
{self.human}

        """
        # TODO: Find better way of showing state in error
        #  state:
        #  \n{state_print}
