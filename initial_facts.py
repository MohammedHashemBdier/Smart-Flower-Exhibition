from facts import GridConfig, Pavilion, NodeCounter, StateNode
from heuristics import calculate_h


def declare_initial(engine):
    engine.declare(GridConfig(max_x=5, max_y=5, warehouse_x=3, warehouse_y=2))

    engine.declare(Pavilion(pavilion_id=1, name="Rose", x=2, y=1, needs=(1,)))
    engine.declare(Pavilion(pavilion_id=2, name="Tulip", x=4, y=3, needs=(1,)))
    engine.declare(Pavilion(pavilion_id=3, name="Orchid", x=1, y=4, needs=(1,)))
    engine.declare(Pavilion(pavilion_id=4, name="Goliat Rose", x=0, y=2, needs=(1,)))

    engine.declare(NodeCounter(next_id=1))

    start_x = 1
    start_y = 3

    p1_needs = (1,)
    p2_needs = (1,)
    p3_needs = (1,)
    p4_needs = (1,)

    initial_h = calculate_h(start_x, start_y, p1_needs, p2_needs, p3_needs, p4_needs)

    engine.declare(StateNode(
        node_id=0,
        parent_id=-1,
        robot_x=start_x,
        robot_y=start_y,
        target_x=3,
        target_y=2,
        carried_pavilion_id=0,
        carried_pavilion_name="",
        carried_load=(),
        p1_needs=p1_needs,
        p2_needs=p2_needs,
        p3_needs=p3_needs,
        p4_needs=p4_needs,
        g=0,
        h=initial_h,
        f=initial_h,
        action="Start at Robot Initial Position",
        status="open",
        printed=False,
    ))
