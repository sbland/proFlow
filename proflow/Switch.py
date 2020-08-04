def switch(gate: str, comment: str = None, options: dict = None, **kwargs):
    opts = {**options, **kwargs} if options else kwargs
    return opts[gate]


__s__ = switch
