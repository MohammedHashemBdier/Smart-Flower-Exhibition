# --- حل مشكلة توافقية مكتبة experta مع إصدارات بايثون الحديثة ---
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping
# -------------------------------------------------------------

from experta import *
from facts import StateNode, GridConfig, ClosedState
from heuristics import calculate_h

class NodeCounter(Fact):
    """حقيقة لتوليد معرفات فريدة للعقد (ID Counter) بدلاً من الحلقات"""
    current_id = Field(int, default=1)

class PavilionConfig(Fact):
    """تخزين مواقع الأجنحة الثابتة في المعرض"""
    pavilion_id = Field(int, mandatory=True)
    x = Field(int, mandatory=True)
    y = Field(int, mandatory=True)

class SolutionPath(Fact):
    """حقيقة لتفعيل آلية طباعة المسار العكسية البرمجية النظيفة"""
    current_node_id = Field(int, mandatory=True)


class SmartFlowerEngine(KnowledgeEngine):

    # ==========================================
    # 1. قاعدة التحقق من الوصول للهدف (Goal Test)
    # ==========================================
    @Rule(
        AS.node << StateNode(
            node_id=MATCH.nid,
            status="active",
            p1_needs=(0, 0, 0),
            p2_needs=(0, 0),
            p3_needs=(0, 0),
            p4_needs=(0, 0)
        ),
        salience=200
    )
    def goal_reached(self, node, nid):
        print("\n==============================================")
        print("🎉 SUCCESS: Optimal solution path found via A*!")
        print("==============================================\n")
        self.declare(SolutionPath(current_node_id=nid))
        self.modify(node, status="closed")

    # ==========================================
    # 2. قاعدة اختيار العقدة الأفضل للاستكشاف (A* Selection)
    # ==========================================
    @Rule(
        AS.node << StateNode(node_id=MATCH.nid, status="open", f=MATCH.f1,
                             robot_x=MATCH.rx, robot_y=MATCH.ry,
                             p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        NOT(StateNode(status="open", f=MATCH.f2 & TEST(lambda f1, f2: f2 < f1))),
        salience=150
    )
    def expand_best_node(self, node, rx, ry, p1n, p2n, p3n, p4n):
        # تسجيل الحالة الحالية في القائمة المغلقة لمنع العودة إليها
        self.declare(ClosedState(robot_x=rx, robot_y=ry, p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n))
        self.modify(node, status="active")

    # ==========================================
    # 3. قواعد الحركة الذكية المميّزة بحظر التكرار
    # ==========================================
    
    @Rule(
        StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, node_id=MATCH.nid, g=MATCH.g_val,
                  p1_carried=MATCH.p1c, p2_carried=MATCH.p2c, p3_carried=MATCH.p3c, p4_carried=MATCH.p4c,
                  p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        GridConfig(max_x=MATCH.mx),
        TEST(lambda rx, mx: rx < mx),
        # شرط حظر التكرار: نمنع التوسع إذا كانت الخلية القادمة تم استكشافها سابقاً بنفس الاحتياجات
        NOT(ClosedState(robot_x=MATCH.nrx & TEST(lambda rx, nrx: nrx == rx + 1), robot_y=MATCH.ry,
                        p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(current_id=MATCH.cid),
        salience=100
    )
    def move_right(self, nid, g_val, rx, ry, p1c, p2c, p3c, p4c, p1n, p2n, p3n, p4n, counter, cid):
        new_h = calculate_h(rx + 1, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(
            node_id=cid, parent_id=nid, robot_x=rx + 1, robot_y=ry,
            p1_carried=p1c, p2_carried=p2c, p3_carried=p3c, p4_carried=p4c,
            p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n,
            g=g_val + 1, h=new_h, f=(g_val + 1) + new_h, action="Move Right", status="open"
        ))
        self.modify(counter, current_id=cid + 1)

    @Rule(
        StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, node_id=MATCH.nid, g=MATCH.g_val,
                  p1_carried=MATCH.p1c, p2_carried=MATCH.p2c, p3_carried=MATCH.p3c, p4_carried=MATCH.p4c,
                  p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        TEST(lambda rx: rx > 0),
        NOT(ClosedState(robot_x=MATCH.nrx & TEST(lambda rx, nrx: nrx == rx - 1), robot_y=MATCH.ry,
                        p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(current_id=MATCH.cid),
        salience=100
    )
    def move_left(self, nid, g_val, rx, ry, p1c, p2c, p3c, p4c, p1n, p2n, p3n, p4n, counter, cid):
        new_h = calculate_h(rx - 1, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(
            node_id=cid, parent_id=nid, robot_x=rx - 1, robot_y=ry,
            p1_carried=p1c, p2_carried=p2c, p3_carried=p3c, p4_carried=p4c,
            p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n,
            g=g_val + 1, h=new_h, f=(g_val + 1) + new_h, action="Move Left", status="open"
        ))
        self.modify(counter, current_id=cid + 1)

    @Rule(
        StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, node_id=MATCH.nid, g=MATCH.g_val,
                  p1_carried=MATCH.p1c, p2_carried=MATCH.p2c, p3_carried=MATCH.p3c, p4_carried=MATCH.p4c,
                  p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        GridConfig(max_y=MATCH.my),
        TEST(lambda ry, my: ry < my),
        NOT(ClosedState(robot_x=MATCH.rx, robot_y=MATCH.nry & TEST(lambda ry, nry: nry == ry + 1),
                        p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(current_id=MATCH.cid),
        salience=100
    )
    def move_up(self, nid, g_val, rx, ry, p1c, p2c, p3c, p4c, p1n, p2n, p3n, p4n, counter, cid):
        new_h = calculate_h(rx, ry + 1, p1n, p2n, p3n, p4n)
        self.declare(StateNode(
            node_id=cid, parent_id=nid, robot_x=rx, robot_y=ry + 1,
            p1_carried=p1c, p2_carried=p2c, p3_carried=p3c, p4_carried=p4c,
            p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n,
            g=g_val + 1, h=new_h, f=(g_val + 1) + new_h, action="Move Up", status="open"
        ))
        self.modify(counter, current_id=cid + 1)

    @Rule(
        StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, node_id=MATCH.nid, g=MATCH.g_val,
                  p1_carried=MATCH.p1c, p2_carried=MATCH.p2c, p3_carried=MATCH.p3c, p4_carried=MATCH.p4c,
                  p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        TEST(lambda ry: ry > 0),
        NOT(ClosedState(robot_x=MATCH.rx, robot_y=MATCH.nry & TEST(lambda ry, nry: nry == ry - 1),
                        p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n)),
        AS.counter << NodeCounter(current_id=MATCH.cid),
        salience=100
    )
    def move_down(self, nid, g_val, rx, ry, p1c, p2c, p3c, p4c, p1n, p2n, p3n, p4n, counter, cid):
        new_h = calculate_h(rx, ry - 1, p1n, p2n, p3n, p4n)
        self.declare(StateNode(
            node_id=cid, parent_id=nid, robot_x=rx, ry=ry - 1,
            p1_carried=p1c, p2_carried=p2c, p3_carried=p3c, p4_carried=p4c,
            p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n,
            g=g_val + 1, h=new_h, f=(g_val + 1) + new_h, action="Move Down", status="open"
        ))
        self.modify(counter, current_id=cid + 1)

    # ==========================================
    # 4. قاعدة تحميل الباقات من المستودع
    # ==========================================
    @Rule(
        StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, node_id=MATCH.nid, g=MATCH.g_val,
                  p1_carried=(0,0,0), p2_carried=(0,0), p3_carried=(0,0), p4_carried=(0,0),
                  p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        GridConfig(warehouse_x=MATCH.wx, warehouse_y=MATCH.wy),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),
        TEST(lambda p1n, p2n, p3n, p4n: sum(p1n) + sum(p2n) + sum(p3n) + sum(p4n) > 0),
        AS.counter << NodeCounter(current_id=MATCH.cid),
        salience=110
    )
    def load_bouquets(self, nid, g_val, rx, ry, p1n, p2n, p3n, p4n, counter, cid):
        new_h = calculate_h(rx, ry, p1n, p2n, p3n, p4n)
        self.declare(StateNode(
            node_id=cid, parent_id=nid, robot_x=rx, robot_y=ry,
            p1_carried=p1n, p2_carried=p2n, p3_carried=p3n, p4_carried=p4n,
            p1_needs=p1n, p2_needs=p2n, p3_needs=p3n, p4_needs=p4n,
            g=g_val + 1, h=new_h, f=(g_val + 1) + new_h, action="Load Bouquets from Warehouse", status="open"
        ))
        self.modify(counter, current_id=cid + 1)

    # ==========================================
    # 5. قاعدة تفريغ الباقات في الأجنحة
    # ==========================================
    @Rule(
        StateNode(status="active", robot_x=MATCH.rx, robot_y=MATCH.ry, node_id=MATCH.nid, g=MATCH.g_val,
                  p1_carried=MATCH.p1c, p2_carried=MATCH.p2c, p3_carried=MATCH.p3c, p4_carried=MATCH.p4c,
                  p1_needs=MATCH.p1n, p2_needs=MATCH.p2n, p3_needs=MATCH.p3n, p4_needs=MATCH.p4n),
        PavilionConfig(pavilion_id=MATCH.pid, x=MATCH.px, y=MATCH.py),
        TEST(lambda rx, ry, px, py: rx == px and ry == py),
        TEST(lambda pid, p1c, p2c, p3c, p4c: 
             (pid == 1 and sum(p1c) > 0) or (pid == 2 and sum(p2c) > 0) or 
             (pid == 3 and sum(p3c) > 0) or (pid == 4 and sum(p4c) > 0)),
        AS.counter << NodeCounter(current_id=MATCH.cid),
        salience=120
    )
    def unload_bouquets(self, nid, g_val, rx, ry, p1c, p2c, p3c, p4c, p1n, p2n, p3n, p4n, pid, counter, cid):
        new_p1n = (0, 0, 0) if pid == 1 else p1n
        new_p1c = (0, 0, 0) if pid == 1 else p1c
        new_p2n = (0, 0) if pid == 2 else p2n
        new_p2c = (0, 0) if pid == 2 else p2c
        new_p3n = (0, 0) if pid == 3 else p3n
        new_p3c = (0, 0) if pid == 3 else p3c
        new_p4n = (0, 0) if pid == 4 else p4n
        new_p4c = (0, 0) if pid == 4 else p4c

        new_h = calculate_h(rx, ry, new_p1n, new_p2n, new_p3n, new_p4n)
        
        self.declare(StateNode(
            node_id=cid, parent_id=nid, robot_x=rx, robot_y=ry,
            p1_carried=new_p1c, p2_carried=new_p2c, p3_carried=new_p3c, p4_carried=new_p4c,
            p1_needs=new_p1n, p2_needs=new_p2n, p3_needs=new_p3n, p4_needs=new_p4n,
            g=g_val + 1, h=new_h, f=(g_val + 1) + new_h, action=f"Unload Bouquets at Pavilion {pid}", status="open"
        ))
        self.modify(counter, current_id=cid + 1)

    # ==========================================
    # 6. قاعدة إغلاق العقدة المستهلكة
    # ==========================================
    @Rule(
        AS.node << StateNode(status="active"),
        salience=10
    )
    def close_node(self, node):
        self.modify(node, status="closed")

    # ==========================================
    # 7. قواعد الطباعة التراجعية العكسية
    # ==========================================
    @Rule(
        AS.path << SolutionPath(current_node_id=MATCH.nid),
        StateNode(node_id=MATCH.nid, parent_id=MATCH.pid & TEST(lambda pid: pid != -1), action=MATCH.act),
        salience=500
    )
    def print_path_step(self, path, pid, act):
        print(f"👉 [Step] Action executed: {act}")
        self.declare(SolutionPath(current_node_id=pid))
        self.retract(path)

    @Rule(
        AS.path << SolutionPath(current_node_id=MATCH.nid),
        StateNode(node_id=MATCH.nid, parent_id=-1, action=MATCH.act),
        salience=500
    )
    def print_path_start(self, path, act):
        print(f"🏁 [Start State]: {act}")
        print("\n==============================================")
        print("🎯 Done! Optimal Path Printed Completely with 0 Loops!")
        print("==============================================")
        self.retract(path)
        self.halt()