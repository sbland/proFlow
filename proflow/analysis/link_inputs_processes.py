from collections import namedtuple
from vendor.polyviz.bezier import bezier_curve_4pt


def get_all_unique_inputs(processes):
    inputs_list = list(set([inp.from_ for p in processes for inp in p.state_inputs] +
                           [inp.as_ for p in processes for inp in p.state_outputs]))
    return inputs_list


def get_inputs_map(inputs_list):
    return dict((inp, i) for i, inp in enumerate(inputs_list))


def get_links(inputs_map, process):
    Output = namedtuple('Output', 'comment input_links output_links')
    input_links = [inputs_map[ip.from_] for ip in process.state_inputs]
    # input_links = [ip.from_ for ip in p.state_inputs]
    output_links = [inputs_map[ip.as_] for ip in process.state_outputs]
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


def link_processes_to_state(canvas, processes):
    Rect_Params = namedtuple('Rect_Params', 'x y w h')

    process_x_pos = 10
    process_width = 100
    process_height = 100

    state_x_pos = 300
    state_width = 100
    state_height = 100

    unique_inputs = get_all_unique_inputs(processes)
    inputs_map = get_inputs_map(unique_inputs)
    links = [get_links(inputs_map, p) for p in processes]

    process_rects = [
        Rect_Params(process_x_pos, ((process_height + 20) * i) +
                    10, process_width, process_height) for i in range(len(processes))]
    state_item_rects = [
        Rect_Params(state_x_pos, ((state_height + 20) * i) +
                    10, state_width, state_height) for i in range(len(unique_inputs))]

    for p in process_rects:
        canvas.stroke_rect(*p)
    for p in state_item_rects:
        canvas.stroke_rect(*p)

    for i, p in enumerate(processes):
        process_rect = process_rects[i]
        canvas.fill_text(p.comment, process_rect.x + 5, process_rect.y + 20)

    for i, p in enumerate(unique_inputs):
        state_item_rect = state_item_rects[i]
        canvas.fill_text(p, state_item_rect.x + 5, state_item_rect.y + 20)

    for i, link in enumerate(links):
        process_rect = process_rects[i]
        for j in link[1]:
            state_rect = state_item_rects[j]
            canvas.stroke_style = 'blue'
            p_start = [process_rect.x + process_rect.w, process_rect.y + 10]
            p_end = [state_rect.x, state_rect.y + 10*i]
            bezier_curve_canvas(canvas, p_start, p_end)

        for j in link[2]:
            state_rect = state_item_rects[j]
            canvas.stroke_style = 'red'
            p_start = [process_rect.x + process_rect.w, process_rect.y + process_rect.h - 10]
            p_end = [state_rect.x, state_rect.y + 10 * i]
            bezier_curve_canvas(canvas, p_start, p_end)

    return canvas
