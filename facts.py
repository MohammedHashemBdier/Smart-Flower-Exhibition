from experta import Fact, Field


class GridConfig(Fact):
    """إعدادات شبكة المعرض وحدود الحركة."""

    max_x = Field(int, mandatory=True)
    max_y = Field(int, mandatory=True)
    warehouse_x = Field(int, mandatory=True)
    warehouse_y = Field(int, mandatory=True)


class Pavilion(Fact):
    """وصف جناح واحد داخل المعرض."""

    pavilion_id = Field(int, mandatory=True)
    name = Field(str, mandatory=True)
    x = Field(int, mandatory=True)
    y = Field(int, mandatory=True)
    needs = Field(tuple, mandatory=True)


class StateNode(Fact):
    """عقدة في شجرة البحث تمثل حالة الروبوت والمستودع والأجنحة."""

    node_id = Field(int, mandatory=True)
    parent_id = Field(int, default=-1)
    robot_x = Field(int, mandatory=True)
    robot_y = Field(int, mandatory=True)
    target_x = Field(int, mandatory=True)
    target_y = Field(int, mandatory=True)
    carried_pavilion_id = Field(int, default=0)
    carried_pavilion_name = Field(str, default="")
    carried_load = Field(tuple, default=())
    p1_needs = Field(tuple, mandatory=True)
    p2_needs = Field(tuple, mandatory=True)
    p3_needs = Field(tuple, mandatory=True)
    p4_needs = Field(tuple, mandatory=True)
    g = Field(int, default=0)
    h = Field(int, default=0)
    f = Field(int, default=0)
    action = Field(str, default="Initial")
    status = Field(str, default="open")
    printed = Field(bool, default=False)


class NodeCounter(Fact):
    """عداد متسلسل لمعرفات العقد الجديدة."""

    next_id = Field(int, default=1)


class ClosedState(Fact):
    """حالة مغلقة لمنع تكرار التوسيع."""

    robot_x = Field(int, mandatory=True)
    robot_y = Field(int, mandatory=True)
    target_x = Field(int, mandatory=True)
    target_y = Field(int, mandatory=True)
    carried_pavilion_id = Field(int, mandatory=True)
    p1_needs = Field(tuple, mandatory=True)
    p2_needs = Field(tuple, mandatory=True)
    p3_needs = Field(tuple, mandatory=True)
    p4_needs = Field(tuple, mandatory=True)


class SolutionPath(Fact):
    """مؤشر لطباعة المسار النهائي بشكل تراجعي."""

    current_node_id = Field(int, mandatory=True)