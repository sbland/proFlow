from collections import namedtuple

from proflow.analysis.network.process_state import (
    ProcessStateNetwork,
    processes_to_state_network,
)
from proflow.objects.process import Process
from vendor.polyviz.bezier import bezier_curve_4pt


def bezier_curve_canvas(canvas, p_start, p_end):
    canvas.line_join = "bevel"
    canvas.line_cap = "round"
    canvas.begin_path()

    points = bezier_curve_4pt(p_start[0], p_start[1], p_end[0], p_end[1], 50)
    canvas.move_to(*points[0])
    for pt in points[1:]:
        canvas.line_to(*pt)
    canvas.stroke()


def t_wrap(text: str, max_length: int = 4) -> str:
    if len(text) <= max_length:
        return text
    chunk_count = len(text) // max_length
    text_rows = [
        text[i * max_length : (i * max_length) + max_length] for i in range(chunk_count + 1)
    ]
    return "\n-".join(text_rows)


def link_processes_to_state(
    canvas,
    processes: list[Process],
    seperation: int = 300,
    process_node_width: int = 200,
    process_node_height: int = 70,
    state_node_width: int = 200,
    state_node_height: int = 100,
    LP: int = 5,  # left padding
    TP: int = 5,  # top padding
    FONT_SIZE: int = 12,
    filter_state_string: str = ".*",
):
    network = processes_to_state_network(processes, filter_state_string)
    return render_process_state_network(
        canvas,
        processes,
        network,
        seperation=seperation,
        process_node_width=process_node_width,
        process_node_height=process_node_height,
        state_node_width=state_node_width,
        state_node_height=state_node_height,
        LP=LP,
        TP=TP,
        FONT_SIZE=FONT_SIZE,
    )


def render_process_state_network(
    canvas,
    processes: list[Process],
    network: ProcessStateNetwork,
    seperation: int = 300,
    process_node_width: int = 200,
    process_node_height: int = 70,
    state_node_width: int = 200,
    state_node_height: int = 100,
    LP: int = 5,
    TP: int = 5,
    FONT_SIZE: int = 12,
):
    HALF_FONT_SIZE = FONT_SIZE // 2

    canvas.font = f"{FONT_SIZE}px sans-serif"
    Rect_Params = namedtuple("Rect_Params", "x y w h")

    process_x_pos = LP
    p_width = process_node_width
    p_height = process_node_height

    state_x_pos = process_x_pos + p_width + seperation
    s_width = state_node_width
    state_height = state_node_height

    y_s_input_offset = state_height / len(processes)

    process_rects = [
        Rect_Params(process_x_pos, ((p_height + TP) * i) + TP, p_width, p_height)
        for i in range(len(processes))
    ]
    state_item_rects = [
        Rect_Params(state_x_pos, ((state_height + TP) * i) + TP, s_width, state_height)
        for i in range(len(network.state_keys))
    ]

    for p in process_rects:
        canvas.stroke_rect(*p)
    for p in state_item_rects:
        canvas.stroke_rect(*p)

    for i, p in enumerate(processes):
        process_rect = process_rects[i]
        text = p.func.__name__ + "\n" + t_wrap(p.comment, p_width // HALF_FONT_SIZE)
        [
            canvas.fill_text(
                t, process_rect.x + LP, (process_rect.y + TP + FONT_SIZE) + FONT_SIZE * i
            )
            for i, t in enumerate(text.split("\n"))
        ]

    for i, p in enumerate(network.state_keys):
        state_item_rect = state_item_rects[i]
        text = "\n".join([t_wrap(t, p_width // HALF_FONT_SIZE) for t in p.split(".")])
        [
            canvas.fill_text(
                t, state_item_rect.x + LP, (state_item_rect.y + TP + FONT_SIZE) + FONT_SIZE * i
            )
            for i, t in enumerate(text.split("\n"))
        ]

    for i, (input_links, output_links) in enumerate(
        zip(network.input_links, network.output_links, strict=True)
    ):
        process_rect = process_rects[i]
        for j in input_links:
            state_rect = state_item_rects[j]
            canvas.stroke_style = "blue"
            p_start = [process_rect.x + process_rect.w, process_rect.y + 10]
            p_end = [state_rect.x, state_rect.y + y_s_input_offset * i]
            bezier_curve_canvas(canvas, p_start, p_end)

        for j in output_links:
            state_rect = state_item_rects[j]
            canvas.stroke_style = "red"
            p_start = [process_rect.x + process_rect.w, process_rect.y + process_rect.h - 10]
            p_end = [state_rect.x, state_rect.y + y_s_input_offset * i]
            bezier_curve_canvas(canvas, p_start, p_end)

    return canvas
