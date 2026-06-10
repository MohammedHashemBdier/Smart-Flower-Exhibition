import collections
import collections.abc

collections.Mapping = collections.abc.Mapping

from experta import AS, KnowledgeEngine, MATCH, NOT, Rule, TEST, DefFacts

from facts import ClosedState, GridConfig, NodeCounter, Pavilion, PossibleMixedLoad, SolutionPath, StateNode, MaxLoad
from heuristics import all_needs_zero, best_pavilion_id, calculate_h, carried_total, has_invalid_coordinates


class SmartFlowerEngine(KnowledgeEngine):
    @DefFacts()
    def _initial_facts(self):
        yield GridConfig(max_x=5, max_y=5, warehouse_x=2, warehouse_y=3)
        yield Pavilion(pavilion_id=1, name="Rose", x=4, y=2, needs=(2, 1, 1))
        yield Pavilion(pavilion_id=2, name="Tulip", x=3, y=4, needs=(3, 1, 0))
        yield Pavilion(pavilion_id=3, name="Orchid", x=5, y=4, needs=(2, 1, 0))
        yield Pavilion(pavilion_id=4, name="Goliat Rose", x=2, y=5, needs=(2, 2, 0))
        yield NodeCounter(next_id=1)

        start_x = 1
        start_y = 3
        p1_needs = (2, 1, 1)
        p2_needs = (3, 1, 0)
        p3_needs = (2, 1, 0)
        p4_needs = (2, 2, 0)
        initial_h = calculate_h(start_x, start_y, p1_needs, p2_needs, p3_needs, p4_needs)
        max_load = max(sum(p1_needs), sum(p2_needs), sum(p3_needs), sum(p4_needs))
        yield MaxLoad(value=max_load)

        yield StateNode(
            node_id=0, parent_id=-1,
            robot_x=start_x, robot_y=start_y,
            target_x=2, target_y=3,
            carried_pavilion_id=0, carried_pavilion_name="", carried_load=(),
            p1_needs=p1_needs, p2_needs=p2_needs, p3_needs=p3_needs, p4_needs=p4_needs,
            g=0, h=initial_h, f=initial_h,
            action="Start at Robot Initial Position",
            status="open", printed=False,
        )

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        MaxLoad(value=MATCH.max_load),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        PossibleMixedLoad(load=MATCH.load),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=279,
    )
    def load_same_color(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, load, counter, next_id, max_load):
        from heuristics import calculate_h
        total_qty = sum(q for _, _, q in load)
        if total_qty > max_load:
            self.modify(node, status="closed")
            return
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(
            node_id=next_id, parent_id=nid,
            robot_x=rx, robot_y=ry,
            target_x=2, target_y=3,  # العودة إلى المستودع بعد التحميل المختلط (سيتم تغييره لاحقاً عند التفريغ)
            carried_pavilion_id=0, carried_pavilion_name="Mixed",
            carried_load=load,
            p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n,
            g=g+1, h=new_h, f=(g+1)+new_h,
            action="Load Same-Color Mixed Batch", status="open", printed=False
        ))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=MATCH.load),
        Pavilion(pavilion_id=MATCH.pid, x=MATCH.px, y=MATCH.py, name=MATCH.name),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: len(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=259,
    )
    def unload_mixed_load(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, load, pid, name, counter, next_id):
        from heuristics import deduct_load_from_needs, calculate_h
        if pid == 1:
            needs = p1n
        elif pid == 2:
            needs = p2n
        elif pid == 3:
            needs = p3n
        else:
            needs = p4n
        new_load, new_needs = deduct_load_from_needs(load, needs, pid)
        if pid == 1:
            new_p1, new_p2, new_p3, new_p4 = new_needs, p2n, p3n, p4n
        elif pid == 2:
            new_p1, new_p2, new_p3, new_p4 = p1n, new_needs, p3n, p4n
        elif pid == 3:
            new_p1, new_p2, new_p3, new_p4 = p1n, p2n, new_needs, p4n
        else:
            new_p1, new_p2, new_p3, new_p4 = p1n, p2n, p3n, new_needs
        new_h = calculate_h(rx, ry, new_p1, new_p2, new_p3, new_p4)
        self.declare(StateNode(
            node_id=next_id, parent_id=nid,
            robot_x=rx, robot_y=ry,
            target_x=2, target_y=3,   # العودة إلى المستودع بعد التفريغ
            carried_pavilion_id=0, carried_pavilion_name="Mixed",
            carried_load=new_load,
            p1_needs=new_p1, p2_needs=new_p2, p3_needs=new_p3, p4_needs=new_p4,
            g=g+1, h=new_h, f=(g+1)+new_h,
            action=f"Unload Mixed Batch at {name}", status="open", printed=False
        ))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(
            node_id=MATCH.nid, status="active",
            robot_x=MATCH.rx, robot_y=MATCH.ry,
            target_x=MATCH.tx, target_y=MATCH.ty,
            g=MATCH.g, h=MATCH.h, f=MATCH.f,
            carried_pavilion_id=MATCH.cpid,
            carried_load=(),
            p1_needs=(0,0,0), p2_needs=(0,0,0), p3_needs=(0,0,0), p4_needs=(0,0,0),
        ),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=500,
    )
    def goal_reached(self, node, counter, nid, rx, ry, tx, ty, g, h, f, cpid, next_id):
        steps = g
        generated_nodes = next_id - 1
        print("\n==============================================")
        print("Solution Report")
        print("==============================================")
        print("Success: all pavilion demands were satisfied.")
        print("Goal status: all pavilion demands were satisfied.")
        print("Overview:")
        print(f"- Steps: {steps}")
        print(f"- Cost: {g}")
        print(f"- Generated nodes: {generated_nodes}")
        print(f"- Final robot position: ({rx},{ry})")
        print(f"- Warehouse / target position: ({tx},{ty})")
        print(f"- Final carried load: pavilion_id={cpid}")
        print("- End state: all pavilion needs are zero and the robot is empty.")
        print("==============================================\n")
        self.declare(SolutionPath(current_node_id=nid))
        self.modify(node, status="closed", carried_pavilion_id=cpid, robot_x=rx, robot_y=ry, target_x=tx, target_y=ty)

    @Rule(
        AS.node << StateNode(
            node_id=MATCH.nid, status="open",
            f=MATCH.f1,
            robot_x=MATCH.rx, robot_y=MATCH.ry,
            target_x=MATCH.tx, target_y=MATCH.ty,
            carried_pavilion_id=MATCH.cpid,
            p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n,
        ),
        NOT(StateNode(status="open", f=MATCH.f2 & TEST(lambda f1, f2: f2 < f1))),
        salience=400,
    )
    def activate_best_node(self, node, rx, ry, tx, ty, cpid, p1n, p2n, p3n, p4n):
        try:
            nid = node.node_id
            fval = getattr(node, 'f', None)
            print(f"[Activate] node={nid} f={fval} pos=({rx},{ry}) target=({tx},{ty}) carry={cpid}")
        except Exception:
            pass
        self.declare(ClosedState(robot_x=rx, robot_y=ry, target_x=tx, target_y=ty, carried_pavilion_id=cpid, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n))
        self.modify(node, status="active")

    @Rule(
        AS.node << StateNode(status="open", printed=False, node_id=MATCH.nid, parent_id=MATCH.pid, robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, g=MATCH.g, h=MATCH.h, f=MATCH.f, action=MATCH.action, carried_pavilion_name=MATCH.cname),
        salience=450,
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
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=new_x, robot_y=ry, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Move Right", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
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
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=new_x, robot_y=ry, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Move Left", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
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
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=new_y, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Move Up", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
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
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=new_y, target_x=tx, target_y=ty, carried_pavilion_id=cpid, carried_pavilion_name=self._carried_name(cpid), carried_load=load, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Move Down", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    # قواعد التحميل (نفس النوع) – تم تصحيحها: لا يتم تصفير الاحتياجات
    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=1, x=MATCH.px, y=MATCH.py, name=MATCH.name1, needs=MATCH.need1),
        MaxLoad(value=MATCH.max_load),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need1: sum(need1) > 0),
        TEST(lambda need1, max_load: sum(need1) <= max_load),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 1),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_1(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name1, need1, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, p4n)   # الاحتياجات تبقى كما هي
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=1, carried_pavilion_name=name1, carried_load=need1, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Load Rose Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=2, x=MATCH.px, y=MATCH.py, name=MATCH.name2, needs=MATCH.need2),
        MaxLoad(value=MATCH.max_load),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need2: sum(need2) > 0),
        TEST(lambda need2, max_load: sum(need2) <= max_load),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 2),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_2(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name2, need2, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=2, carried_pavilion_name=name2, carried_load=need2, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Load Tulip Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=3, x=MATCH.px, y=MATCH.py, name=MATCH.name3, needs=MATCH.need3),
        MaxLoad(value=MATCH.max_load),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need3: sum(need3) > 0),
        TEST(lambda need3, max_load: sum(need3) <= max_load),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 3),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_3(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name3, need3, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=3, carried_pavilion_name=name3, carried_load=need3, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Load Orchid Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=0, carried_load=()),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        Pavilion(pavilion_id=4, x=MATCH.px, y=MATCH.py, name=MATCH.name4, needs=MATCH.need4),
        MaxLoad(value=MATCH.max_load),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda need4: sum(need4) > 0),
        TEST(lambda need4, max_load: sum(need4) <= max_load),
        TEST(lambda rx, ry, p1n, p2n, p3n, p4n: best_pavilion_id(rx, ry, p1n, p2n, p3n, p4n) == 4),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=280,
    )
    def load_pavilion_4(self, node, nid, g, rx, ry, p1n, p2n, p3n, p4n, px, py, name4, need4, counter, next_id):
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=px, target_y=py, carried_pavilion_id=4, carried_pavilion_name=name4, carried_load=need4, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action="Load Goliat Rose Batch", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    # قواعد التفريغ (نفس النوع) – مع target_x=2, target_y=3
    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=1, carried_load=MATCH.load),
        Pavilion(pavilion_id=1, x=MATCH.px, y=MATCH.py, name=MATCH.name1),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_1(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, load, name1, counter, next_id):
        new_p1 = tuple(map(lambda ab: max(ab[0] - ab[1], 0), zip(p1n, load)))
        new_h = calculate_h(rx, ry, new_p1, p2n, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=2, target_y=3, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=new_p1, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action=f"Unload Rose Batch at {name1}", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=2, carried_load=MATCH.load),
        Pavilion(pavilion_id=2, x=MATCH.px, y=MATCH.py, name=MATCH.name2),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_2(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, load, name2, counter, next_id):
        new_p2 = tuple(map(lambda ab: max(ab[0] - ab[1], 0), zip(p2n, load)))
        new_h = calculate_h(rx, ry, p1n, new_p2, p3n, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=2, target_y=3, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=p1n, p2_needs=new_p2, p3_needs=p3n, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action=f"Unload Tulip Batch at {name2}", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=3, carried_load=MATCH.load),
        Pavilion(pavilion_id=3, x=MATCH.px, y=MATCH.py, name=MATCH.name3),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_3(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, load, name3, counter, next_id):
        new_p3 = tuple(map(lambda ab: max(ab[0] - ab[1], 0), zip(p3n, load)))
        new_h = calculate_h(rx, ry, p1n, p2n, new_p3, p4n)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=2, target_y=3, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=p1n, p2_needs=p2n, p3_needs=new_p3, p4_needs=p4n, g=g+1, h=new_h, f=(g+1)+new_h, action=f"Unload Orchid Batch at {name3}", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    @Rule(
        AS.node << StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, target_x=MATCH.tx, target_y=MATCH.ty, node_id=MATCH.nid, g=MATCH.g, p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n, carried_pavilion_id=4, carried_load=MATCH.load),
        Pavilion(pavilion_id=4, x=MATCH.px, y=MATCH.py, name=MATCH.name4),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda load: carried_total(load) > 0),
        AS.counter << NodeCounter(next_id=MATCH.next_id),
        salience=260,
    )
    def unload_pavilion_4(self, node, nid, g, rx, ry, tx, ty, p1n, p2n, p3n, p4n, load, name4, counter, next_id):
        new_p4 = tuple(map(lambda ab: max(ab[0] - ab[1], 0), zip(p4n, load)))
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, new_p4)
        self.declare(StateNode(node_id=next_id, parent_id=nid, robot_x=rx, robot_y=ry, target_x=2, target_y=3, carried_pavilion_id=0, carried_pavilion_name="", carried_load=(), p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=new_p4, g=g+1, h=new_h, f=(g+1)+new_h, action=f"Unload Goliat Rose Batch at {name4}", status="open", printed=False))
        self.modify(counter, next_id=next_id+1)
        self.modify(node, status="closed")

    # قواعد المنع والإغلاق
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

    # طباعة المسار
    @Rule(
        AS.path << SolutionPath(current_node_id=MATCH.nid),
        StateNode(node_id=MATCH.nid, parent_id=MATCH.pid, action=MATCH.act),
        TEST(lambda pid: pid != -1),
        salience=700,
    )
    def print_path_step(self, path, pid, act):
        stats = getattr(self, "solution_stats", {})
        stats["path_steps"] = stats.get("path_steps", 0) + 1
        stats["moves"] = stats.get("moves", 0) + int(act.startswith("Move"))
        stats["loads"] = stats.get("loads", 0) + int(act.startswith("Load"))
        stats["unloads"] = stats.get("unloads", 0) + int(act.startswith("Unload"))
        stats["move_right"] = stats.get("move_right", 0) + int(act == "Move Right")
        stats["move_left"] = stats.get("move_left", 0) + int(act == "Move Left")
        stats["move_up"] = stats.get("move_up", 0) + int(act == "Move Up")
        stats["move_down"] = stats.get("move_down", 0) + int(act == "Move Down")
        stats["load_rose"] = stats.get("load_rose", 0) + int(act == "Load Rose Batch")
        stats["load_tulip"] = stats.get("load_tulip", 0) + int(act == "Load Tulip Batch")
        stats["load_orchid"] = stats.get("load_orchid", 0) + int(act == "Load Orchid Batch")
        stats["load_goliat"] = stats.get("load_goliat", 0) + int(act == "Load Goliat Rose Batch")
        stats["unload_rose"] = stats.get("unload_rose", 0) + int(act == "Unload Rose Batch at Rose")
        stats["unload_tulip"] = stats.get("unload_tulip", 0) + int(act == "Unload Tulip Batch at Tulip")
        stats["unload_orchid"] = stats.get("unload_orchid", 0) + int(act == "Unload Orchid Batch at Orchid")
        stats["unload_goliat"] = stats.get("unload_goliat", 0) + int(act == "Unload Goliat Rose Batch at Goliat Rose")
        getattr(self, "solution_path_actions", []).append(act)
        print(f"[Path] {act}")
        self.declare(SolutionPath(current_node_id=pid))
        self.retract(path)

    @Rule(
        AS.path << SolutionPath(current_node_id=MATCH.nid),
        StateNode(node_id=MATCH.nid, parent_id=-1, action=MATCH.act),
        salience=700,
    )
    def print_path_start(self, path, act):
        stats = getattr(self, "solution_stats", {})
        print("Path Summary:")
        print("Action breakdown:")
        print(f"- Moves: {stats.get('moves', 0)}")
        print(f"- Loads: {stats.get('loads', 0)}")
        print(f"- Unloads: {stats.get('unloads', 0)}")
        print(f"- Pavilions served: {stats.get('unloads', 0)}/4")
        print(f"- Warehouse trips: {stats.get('loads', 0)}")
        print(f"- Right/Left/Up/Down: {stats.get('move_right', 0)}/{stats.get('move_left', 0)}/{stats.get('move_up', 0)}/{stats.get('move_down', 0)}")
        print(f"- Rose/Tulip/Orchid/Goliat loads: {stats.get('load_rose', 0)}/{stats.get('load_tulip', 0)}/{stats.get('load_orchid', 0)}/{stats.get('load_goliat', 0)}")
        print(f"- Rose/Tulip/Orchid/Goliat unloads: {stats.get('unload_rose', 0)}/{stats.get('unload_tulip', 0)}/{stats.get('unload_orchid', 0)}/{stats.get('unload_goliat', 0)}")
        print(f"[Path] Start -> {act}")
        print("Numbered solution path:")
        solution_path_actions = list(reversed(getattr(self, "solution_path_actions", [])))
        numbered_path = "\n".join(map(lambda pair: f"{pair[0]:02d}. {pair[1]}", enumerate(solution_path_actions, start=1)))
        print(numbered_path)
        print(f"Total solution cost: {stats.get('path_steps', 0)}")
        print("==============================================")
        print("Solution path printed successfully.")
        print("==============================================")
        self.retract(path)
        self.halt()

    def _carried_name(self, pavilion_id):
        names = {0: "", 1: "Rose", 2: "Tulip", 3: "Orchid", 4: "Goliat Rose"}
        return names[pavilion_id]