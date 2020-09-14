from collections import namedtuple
from typing import List
import re

from vendor.polyviz.bezier import bezier_curve_4pt

from proflow.Objects import Process


def get_all_unique_inputs(processes):
    inputs_list = list(set([inp.from_ for p in processes for inp in p.state_inputs])) + \
        list(set([inp.as_ for p in processes for inp in p.state_outputs]))
    unique_inputs = list(set(inputs_list))
    return unique_inputs[::-1]


def get_inputs_map(inputs_list):
    return dict((inp, i) for i, inp in enumerate(inputs_list))


def get_links(inputs_map, process):
    Output = namedtuple('Output', 'comment input_links output_links')
    input_links = [inputs_map[ip.from_] for ip in process.state_inputs if ip.from_ in inputs_map]
    # input_links = [ip.from_ for ip in p.state_inputs]
    output_links = [inputs_map[ip.as_] for ip in process.state_outputs if ip.as_ in inputs_map]
    # output_links = [ip.as_ for ip in p.state_outputs]
    return Output(process.comment, input_links, output_links)


def bezier_curve_canvas(canvas, p_start, p_end):
    canvas.line_join = 'bevel'
    canvas.line_cap = 'round'
    canvas.begin_path()

    points = bezier_curve_4pt(p_start[0], p_start[1], p_end[0], p_end[1], 50)
    canvas.move_to(*points[0])
    for pt in points[1:]:
        canvas.line_to(*pt)
    canvas.stroke()


def t_wrap(text: str, max_length: int = 4) -> str:
    if len(text) <= max_length:
        return text
    chunk_count = len(text)//max_length
    text_rows = [text[i * max_length: (i * max_length) + max_length] for i in range(chunk_count+1)]
    return '\n-'.join(text_rows)


def link_processes_to_state(
        canvas,
        processes: List[Process],
        seperation: int = 300,
        process_node_width: int = 200,
        process_node_height: int = 70,
        state_node_width: int = 200,
        state_node_height: int = 100,
        LP: int = 5,  # left padding
        TP: int = 5,  # top padding
        FONT_SIZE: int = 12,
        filter_state_string: str = '.*',
):
    HALF_FONT_SIZE = FONT_SIZE // 2

    canvas.font = f'{FONT_SIZE}px sans-serif'
    Rect_Params = namedtuple('Rect_Params', 'x y w h')

    process_x_pos = LP
    p_width = process_node_width
    p_height = process_node_height

    state_x_pos = process_x_pos + p_width + seperation
    s_width = state_node_width
    state_height = state_node_height

    y_s_input_offset = (state_height / len(processes))

    unique_inputs = get_all_unique_inputs(processes)
    filter_re = filter_state_string if type(filter_state_string) == re.Pattern \
        else re.compile(f'.*{filter_state_string}.*' or '.*')
    filtered_inputs = [i for i in unique_inputs if filter_re.match(i)]
    inputs_map = get_inputs_map(filtered_inputs)
    links = [get_links(inputs_map, p) for p in processes]

    process_rects = [
        Rect_Params(process_x_pos, ((p_height + TP) * i) +
                    TP, p_width, p_height) for i in range(len(processes))]
    state_item_rects = [
        Rect_Params(state_x_pos, ((state_height + TP) * i) +
                    TP, s_width, state_height) for i in range(len(filtered_inputs))]

    for p in process_rects:
        canvas.stroke_rect(*p)
    for p in state_item_rects:
        canvas.stroke_rect(*p)

    for i, p in enumerate(processes):
        process_rect = process_rects[i]
        text = p.func.__name__ + '\n' + t_wrap(p.comment, p_width//HALF_FONT_SIZE)
        [canvas.fill_text(t, process_rect.x + LP, (process_rect.y + TP + FONT_SIZE) + FONT_SIZE * i)
         for i, t in enumerate(text.split('\n'))]

    for i, p in enumerate(filtered_inputs):
        state_item_rect = state_item_rects[i]
        text = '\n'.join([t_wrap(t, p_width//HALF_FONT_SIZE) for t in p.split('.')])
        [canvas.fill_text(t, state_item_rect.x + LP, (state_item_rect.y + TP + FONT_SIZE) +
                          FONT_SIZE * i)
         for i, t in enumerate(text.split('\n'))]

    for i, link in enumerate(links):
        process_rect = process_rects[i]
        for j in link[1]:
            state_rect = state_item_rects[j]
            canvas.stroke_style = 'blue'
            p_start = [process_rect.x + process_rect.w, process_rect.y + 10]
            p_end = [state_rect.x, state_rect.y + y_s_input_offset*i]
            bezier_curve_canvas(canvas, p_start, p_end)

        for j in link[2]:
            state_rect = state_item_rects[j]
            canvas.stroke_style = 'red'
            p_start = [process_rect.x + process_rect.w, process_rect.y + process_rect.h - 10]
            p_end = [state_rect.x, state_rect.y + y_s_input_offset * i]
            bezier_curve_canvas(canvas, p_start, p_end)

    return canvas


if __name__ == "__main__":
    # Allow relative import
    import os
    import sys
    print(os.path)
    module_path = os.path.abspath(os.path.join('../../vendor'))
    if module_path not in sys.path:
        sys.path.append(module_path)
    module_path = os.path.abspath(os.path.join('../..'))
    if module_path not in sys.path:
        sys.path.append(module_path)

    from proflow.Objects import Process, I
    from ipycanvas import Canvas

    def demo_func(x, y):
        """DEMO FUNC"""
        return x - y

    processes = [
        Process(
            func=lambda x, y, z: x + y + z,
            comment="Demo process a",
            config_inputs=[
                I('foo.bar', as_='x'),
            ],
            state_inputs=[
                I('info.today', as_='y'),
                I('info.hour', as_='z')
            ],
            state_outputs=[
                I('_result', as_='info.tomorrow'),
            ]
        ),
        Process(
            func=lambda x, y, z: x + y + z,
            comment="Demo process a",
            config_inputs=[
                I('foo.bar', as_='x'),
            ],
            state_inputs=[
                I('log.foo', as_='y'),
                I('info.hour', as_='z')
            ],
            state_outputs=[
                I('_result', as_='info.tomorrow'),
            ]
        ),
        Process(
            func=demo_func,
            comment="Demo process b",
            config_inputs=[
                I('foo.bar', as_='x'),
            ],
            state_inputs=[
                I('info.tomorrow', as_='y'),
            ],
            state_outputs=[
                I('_result', as_='info.today'),
            ]
        ),
        Process(
            func=lambda x, y: x + y,
            comment="Demo process c with a really long comment and info",
            config_inputs=[
                I('foo.bar', as_='x'),
            ],
            state_inputs=[
                I('info.tomorrow', as_='y'),
            ],
            state_outputs=[
                I('_result', as_='info.today'),
            ]
        ),
        Process(
            func=lambda x, y: x + y,
            comment="Demo process d",
            config_inputs=[
                I('foo.bar', as_='x'),
            ],
            state_inputs=[
                I('info.today', as_='y'),
            ],
            state_outputs=[
                I('_result', as_='info.tomorrow'),
                I('_result', as_='log.extra'),
            ]
        ),
    ] * 5
    canvas = Canvas(width=1200, height=800)
    link_processes_to_state(canvas, processes, 600)
# canvas
