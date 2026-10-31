from ipycanvas import Canvas

from proflow.analysis.canvas import (
    link_processes_to_state,
)
from proflow.objects.interface import I
from proflow.objects.process import Process

if __name__ == "__main__":
    # Allow relative import
    import os
    import sys

    print(os.path)
    module_path = os.path.abspath(os.path.join("../../vendor"))
    if module_path not in sys.path:
        sys.path.append(module_path)
    module_path = os.path.abspath(os.path.join("../.."))
    if module_path not in sys.path:
        sys.path.append(module_path)

    def demo_func(x, y):
        """DEMO FUNC"""
        return x - y

    processes = [
        Process(
            func=lambda x, y, z: x + y + z,
            comment="Demo process a",
            config_inputs=[
                I("foo.bar", as_="x"),
            ],
            state_inputs=[I("info.today", as_="y"), I("info.hour", as_="z")],
            state_outputs=[
                I("_result", as_="info.tomorrow"),
            ],
        ),
        Process(
            func=lambda x, y, z: x + y + z,
            comment="Demo process a",
            config_inputs=[
                I("foo.bar", as_="x"),
            ],
            state_inputs=[I("log.foo", as_="y"), I("info.hour", as_="z")],
            state_outputs=[
                I("_result", as_="info.tomorrow"),
            ],
        ),
        Process(
            func=demo_func,
            comment="Demo process b",
            config_inputs=[
                I("foo.bar", as_="x"),
            ],
            state_inputs=[
                I("info.tomorrow", as_="y"),
            ],
            state_outputs=[
                I("_result", as_="info.today"),
            ],
        ),
        Process(
            func=lambda x, y: x + y,
            comment="Demo process c with a really long comment and info",
            config_inputs=[
                I("foo.bar", as_="x"),
            ],
            state_inputs=[
                I("info.tomorrow", as_="y"),
            ],
            state_outputs=[
                I("_result", as_="info.today"),
            ],
        ),
        Process(
            func=lambda x, y: x + y,
            comment="Demo process d",
            config_inputs=[
                I("foo.bar", as_="x"),
            ],
            state_inputs=[
                I("info.today", as_="y"),
            ],
            state_outputs=[
                I("_result", as_="info.tomorrow"),
                I("_result", as_="log.extra"),
            ],
        ),
    ] * 5
    canvas = Canvas(width=1200, height=800)
    link_processes_to_state(canvas, processes, 600)
# canvas
