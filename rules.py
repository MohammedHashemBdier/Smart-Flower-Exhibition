import collections
import collections.abc

collections.Mapping = collections.abc.Mapping

from experta import AS, KnowledgeEngine, MATCH, NOT, Rule, TEST

from facts import ClosedState, GridConfig, NodeCounter, Pavilion, SolutionPath, StateNode
from heuristics import all_needs_zero, best_pavilion_id, calculate_h, carried_total, has_invalid_coordinates


class SmartFlowerEngine(KnowledgeEngine):
    @Rule(
        AS.node << StateNode(
            node_id=MATCH.nid,
            status="active",
            robot_x=MATCH.rx,
            robot_y=MATCH.ry,
            target_x=MATCH.tx,
            target_y=MATCH.ty,
            carried_pavilion_id=MATCH.cpid,
            carried_load=(),
            p1_needs=(0, 0, 0),
            p2_needs=(0, 0),
            p3_needs=(0, 0),
            p4_needs=(0, 0),
        ),
        salience=500,
    )
    def goal_reached(self, node, nid, rx, ry, tx, ty, cpid):
        print("\n==============================================")
        print("Success: all pavilion demands were satisfied.")
        print("==============================================\n")
        self.declare(SolutionPath(current_node_id=nid))
        self.modify(node, status="closed", carried_pavilion_id=cpid, robot_x=rx, robot_y=ry, target_x=tx, target_y=ty)

    @Rule(
        AS.node << StateNode(
            node_id=MATCH.nid,
            status="open",
            f=MATCH.f1,
            robot_x=MATCH.rx,
            robot_y=MATCH.ry,
            target_x=MATCH.tx,
            target_y=MATCH.ty,
            carried_pavilion_id=MATCH.cpid,
            p1_needs=MATCH.p1n,
            p2_needs=MATCH.p2n,
            p3_needs=MATCH.p3n,
            p4_needs=MATCH.p4n,
        ),
        NOT(StateNode(status="open", f=MATCH.f2 & TEST(lambda f1, f2: f2 < f1))),
        salience=400,
    )
    def activate_best_node(self, node, rx, ry, tx, ty, cpid, p1n, p2n, p3n, p4n):
        self.declare(ClosedState(robot_x=rx, robot_y=ry, target_x=tx, target_y=ty, carried_pavilion_id=cpid, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n))
        self.modify(node, status="active")

    @Rule(
        AS.node << StateNode(status="open", printed=False, node_id=MATCH.nid, parent_id=MATCH.pid, robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, g=MATCH.g, h=MATCH.h, f=MATCH.f, action=MATCH.action, carried_pavilion_name=MATCH.cname),
        salience=350,
    )
    def print_tree_node(self, node, nid, pid, rx, ry, tx, ty, g, h, f, action, cname):
        print(f"[Tree] id={nid} parent={pid} pos=({rx},{ry}) target=({tx},{ty}) g={g} h={h} f={f} action={action} carry={cname}")
        self.modify(node, printed=True)

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=MATCH.cpid, carried_load=MATCH.load),
        GridConfig(max_x=MATCH.max_x),
        TEST(lambda rx, tx, max_x: (rx < tx) and (rx < max_x)),
        NOT(ClosedState(robot_x=MATCH.nrx & TEST(lambda rx, nrx: nrx == rx + 1), robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, carried_pavilion_id=MATCH.cpid, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=300,
    )
    def move_right(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, cpid, load, counter, next_id):
        new_x = rx + 1
        new_h = calculate_h(new_x, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=new_x, robot_y=ry, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action="Move Right", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=MATCH.cpid, carried_load=MATCH.load),
        TEST(lambda rx, tx: rx > tx),
        NOT(ClosedState(robot_x=MATCH.nrx & TEST(lambda rx, nrx: nrx == rx - 1), robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, carried_pavilion_id=MATCH.cpid, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=300,
    )
    def move_left(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, cpid, load, counter, next_id):
        new_x = rx - 1
        new_h = calculate_h(new_x, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=new_x, robot_y=ry, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action="Move Left", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=MATCH.cpid, carried_load=MATCH.load),
        GridConfig(max_y=MATCH.max_y),
        TEST(lambda rx, tx, ry, ty, max_y: (rx == tx) and (ry < ty) and (ry < max_y)),
        NOT(ClosedState(robot_x=MATCH.rx, robot_y=MATCH.nry & TEST(lambda ry, nry: nry == ry + 1), target_x=MATCH.tx, target_y=MATCH.ty, carried_pavilion_id=MATCH.cpid, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=300,
    )
    def move_up(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, cpid, load, counter, next_id):
        new_y = ry + 1
        new_h = calculate_h(rx, new_y, p1n, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=new_y, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action="Move Up", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=MATCH.cpid, carried_load=MATCH.load),
        TEST(lambda rx, tx, ry, ty: (rx == tx) and (ry > ty)),
        NOT(ClosedState(robot_x=MATCH.rx, robot_y=MATCH.nry & TEST(lambda ry, nry: nry == ry - 1), target_x=MATCH.tx, target_y=MATCH.ty, carried_pavilion_id=MATCH.cpid, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=300,
    )
    def move_down(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, cpid, load, counter, next_id):
        new_y = ry - 1
        new_h = calculate_h(rx, new_y, p1n, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=new_y, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action="Move Down", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=1, x=MATCH.px, y=MATCH.py, name=MATCH.name1, needs=MATCH.need1),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need1: sum(need1) > 0),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 1),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_1(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name1, need1, counter, next_id):
        new_h = calculate_h(rx, ry, (0, 0, 0), p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=1, carried_pavilion_name=name1, carried_load=need1, p1_needs=(0, 0, 0), p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action="Load Rose Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=2, x=MATCH.px, y=MATCH.py, name=MATCH.name2, needs=MATCH.need2),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need2: sum(need2) > 0),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 2),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_2(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name2, need2, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, (0, 0), p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=2, carried_pavilion_name=name2, carried_load=need2, p1_needs=p1n, p2_needs=(0, 0), p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action="Load Tulip Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=3, x=MATCH.px, y=MATCH.py, name=MATCH.name3, needs=MATCH.need3),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need3: sum(need3) > 0),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 3),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_3(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name3, need3, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, (0, 0), p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=3, carried_pavilion_name=name3, carried_load=need3, p1_needs=p1n, p2_needs=p2n, p3_needs=(0, 0), p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action="Load Orchid Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=4, x=MATCH.px, y=MATCH.py, name=MATCH.name4, needs=MATCH.need4),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need4: sum(need4) > 0),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 4),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_4(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name4, need4, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, (0, 0))
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=4, carried_pavilion_name=name4, carried_load=need4, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=(0, 0), g=g + 1, h=new_h, f=(g + 1) + new_h, action="Load Goliat Rose Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=1, carried_load=MATCH.load),
        Pavilion(pavilion_id=1, x=MATCH.px, y=MATCH.py, name=MATCH.name1),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_1(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, name1, counter, next_id):
        new_h = calculate_h(rx, ry, (0, 0, 0), p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=3, target_y=2, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=(0, 0, 0), p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action=f"Unload Rose Batch at {name1}", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=2, carried_load=MATCH.load),
        Pavilion(pavilion_id=2, x=MATCH.px, y=MATCH.py, name=MATCH.name2),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_2(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, name2, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, (0, 0), p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=3, target_y=2, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=p1n, p2_needs=(0, 0), p3_needs=p3n, p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action=f"Unload Tulip Batch at {name2}", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=3, carried_load=MATCH.load),
        Pavilion(pavilion_id=3, x=MATCH.px, y=MATCH.py, name=MATCH.name3),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_3(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, name3, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, (0, 0), p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=3, target_y=2, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=p1n, p2_needs=p2n, p3_needs=(0, 0), p4_needs=p4n, g=g + 1, h=new_h, f=(g + 1) + new_h, action=f"Unload Orchid Batch at {name3}", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=4, carried_load=MATCH.load),
        Pavilion(pavilion_id=4, x=MATCH.px, y=MATCH.py, name=MATCH.name4),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_4(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, name4, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, (0, 0))
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=3, target_y=2, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=(0, 0), g=g + 1, h=new_h, f=(g + 1) + new_h, action=f"Unload Goliat Rose Batch at {name4}", status="open", printed=False))
        self.modify(counter, next_id=next_id + 1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", node_id=MATCH.nid, robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        GridConfig(max_x=MATCH.max_x, max_y=MATCH.max_y),
        TEST(lambda rx, ry, max_x, max_y: has_invalid_coordinates(rx, ry, max_x, max_y)),
        salience=250,
    )
    def prune_invalid_coordinates(self, node, nid):
        print(f"[Prune] Invalid coordinates removed: node {nid}")
        self.retract(node)

    @Rule(
        AS.node << StateNode(status="active", node_id=MATCH.nid, carried_pavilion_id=MATCH.cpid, carried_load=MATCH.load, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        TEST(lambda cpid, load, p1n, p2n, p3n, p4n: (cpid == 0 and carried_total(load) != 0) or (cpid != 0 and carried_total(load) == 0) or (all_needs_zero(p1n, p2n, p3n, p4n) and carried_total(load) != 0)),
        salience=245,
    )
    def prune_invalid_load(self, node, nid):
        print(f"[Prune] Invalid load removed: node {nid}")
        self.retract(node)

    @Rule(
        AS.node << StateNode(status="active"),
        salience=50,
    )
    def close_node(self, node):
        self.modify(node, status="closed")

    @Rule(
        AS.path << SolutionPath(current_node_id=MATCH.nid),
        StateNode(node_id=MATCH.nid, parent_id=MATCH.pid, action=MATCH.act),
        TEST(lambda pid: pid != -1),
        salience=700,
    )
    def print_path_step(self, path, pid, act):
        print(f"[Path] {act}")
        self.declare(SolutionPath(current_node_id=pid))
        self.retract(path)

    @Rule(
        AS.path << SolutionPath(current_node_id=MATCH.nid),
        StateNode(node_id=MATCH.nid, parent_id=-1, action=MATCH.act),
        salience=700,
    )
    def print_path_start(self, path, act):
        print(f"[Path] Start -> {act}")
        print("==============================================")
        print("Solution path printed successfully.")
        print("==============================================")
        self.retract(path)
        self.halt()

    def _carried_name(self, pavilion_id):
        names = {0: "", 1: "Rose", 2: "Tulip", 3: "Orchid", 4: "Goliat Rose"}
        return names[pavilion_id]
