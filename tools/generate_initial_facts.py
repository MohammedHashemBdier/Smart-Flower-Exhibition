"""
Generator: produce initial_facts.py from a JSON game_config file.
This script itself may use loops/ifs (it's a dev tool), but the produced
initial_facts.py contains only explicit `engine.declare(...)` calls
and no control-flow statements, satisfying the submission constraints.

Usage:
    python tools/generate_initial_facts.py --config ../game_config.json --out ../initial_facts.py
"""
import argparse
import json
from pathlib import Path

TEMPLATE_HEADER = '''from facts import GridConfig, Pavilion, NodeCounter, StateNode
from heuristics import calculate_h


def declare_initial(engine):
'''

TEMPLATE_FOOTER = '\n'


def fmt_tuple(t):
    if not t:
        return '()'
    return '(' + ', '.join(str(x) for x in t) + (',' if len(t)==1 else '') + ')'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', default='game_config.json')
    p.add_argument('--out', default='initial_facts.py')
    args = p.parse_args()

    cfg_path = Path(args.config)
    out_path = Path(args.out)

    cfg = json.loads(cfg_path.read_text(encoding='utf-8'))

    lines = [TEMPLATE_HEADER]

    grid = cfg.get('grid', {})
    warehouse = cfg.get('warehouse', {})
    wx = warehouse.get('x', 3)
    wy = warehouse.get('y', 2)
    gw = grid.get('width', 5)
    gh = grid.get('height', 5)

    lines.append(f"    engine.declare(GridConfig(max_x={gw}, max_y={gh}, warehouse_x={wx}, warehouse_y={wy}))\n")
    lines.append('\n')

    pavilions = cfg.get('pavilions', [])

    # write explicit Pavilion declarations
    for i, p in enumerate(pavilions, start=1):
        pid = p.get('id', i)
        name = p.get('name', f'Pavilion_{i}')
        x = p.get('x', 1)
        y = p.get('y', 1)
        need = p.get('need', [])
        if isinstance(need, int):
            need_tpl = (need,)
        else:
            need_tpl = tuple(need)
        need_str = fmt_tuple(need_tpl)
        line = f"    engine.declare(Pavilion(pavilion_id={pid}, name=\"{name}\", x={x}, y={y}, needs={need_str}))\n"
        lines.append(line)

    # ensure at least 4 pavilion declarations (fill empties explicitly)
    if len(pavilions) < 4:
        for i in range(len(pavilions)+1, 5):
            lines.append(f"    engine.declare(Pavilion(pavilion_id={i}, name=\"P{i}\", x=0, y=0, needs=()))\n")

    lines.append('\n')
    lines.append('    engine.declare(NodeCounter(next_id=1))\n')
    lines.append('\n')

    # initial robot state
    robot = cfg.get('robot_start', {})
    sx = robot.get('x', 1)
    sy = robot.get('y', 3)

    # prepare needs for calculate_h
    needs_list = []
    for p in pavilions:
        need = p.get('need', ())
        if isinstance(need, int):
            needs_list.append((need,))
        else:
            needs_list.append(tuple(need))
    while len(needs_list) < 4:
        needs_list.append(())

    p1, p2, p3, p4 = needs_list[:4]

    lines.append(f"    start_x = {sx}\n")
    lines.append(f"    start_y = {sy}\n")
    lines.append('\n')
    lines.append(f"    p1_needs = {fmt_tuple(p1)}\n")
    lines.append(f"    p2_needs = {fmt_tuple(p2)}\n")
    lines.append(f"    p3_needs = {fmt_tuple(p3)}\n")
    lines.append(f"    p4_needs = {fmt_tuple(p4)}\n")
    lines.append('\n')

    # calculate initial_h call as a string (the produced file will call calculate_h)
    lines.append('    initial_h = calculate_h(start_x, start_y, p1_needs, p2_needs, p3_needs, p4_needs)\n')
    lines.append('\n')

    lines.append('    engine.declare(StateNode(\n')
    lines.append('        node_id=0,\n')
    lines.append('        parent_id=-1,\n')
    lines.append('        robot_x=start_x,\n')
    lines.append('        robot_y=start_y,\n')
    lines.append(f'        target_x={wx},\n')
    lines.append(f'        target_y={wy},\n')
    lines.append('        carried_pavilion_id=0,\n')
    lines.append('        carried_pavilion_name="",\n')
    lines.append('        carried_load=(),\n')
    lines.append('        p1_needs=p1_needs,\n')
    lines.append('        p2_needs=p2_needs,\n')
    lines.append('        p3_needs=p3_needs,\n')
    lines.append('        p4_needs=p4_needs,\n')
    lines.append('        g=0,\n')
    lines.append('        h=initial_h,\n')
    lines.append('        f=initial_h,\n')
    lines.append('        action="Start at Robot Initial Position",\n')
    lines.append('        status="open",\n')
    lines.append('        printed=False,\n')
    lines.append('    ))\n')

    content = ''.join(lines)

    out_path.write_text(content, encoding='utf-8')
    print(f'Wrote {out_path}')


if __name__ == '__main__':
    main()
