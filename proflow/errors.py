class Run_Process_Error(Exception):
    def __init__(self, process: 'Process', error: Exception, state):
        self.message = f'Failed to run {process.comment or process.func.__name__}'
        self.error = error
        self.state = state

    def __str__(self):
        state_str = str(self.state)
        state_print = state_str[0:100] + '...' + \
            state_str[:-100] if len(state_str) > 200 else state_str
        return f"""
        !! {self.message} !! \n
        !! {str(self.error)}
         state:
         \n{state_print}
        """
