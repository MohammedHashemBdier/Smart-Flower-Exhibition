from experta import *

class GridConfig(Fact):
    """تخزين الإعدادات الثابتة للشبكة والمستودع لتجنب القيم الصلبة (Hardcoding)"""
    max_x = Field(int, mandatory=True)
    max_y = Field(int, mandatory=True)
    warehouse_x = Field(int, mandatory=True)
    warehouse_y = Field(int, mandatory=True)

class StateNode(Fact):
    """تمثيل عقدة فريدة في شجرة البحث تمثل حالة العالم بالكامل في لحظة ما"""
    node_id = Field(int, mandatory=True)       # معرف فريد للعقدة
    parent_id = Field(int, default=-1)         # معرف العقدة الأب لتتبع مسار الحل
    
    # موقع الروبوت الحالي في هذه العقدة
    robot_x = Field(int, mandatory=True)
    robot_y = Field(int, mandatory=True)
    
    # حمولة الروبوت الحالية من الباقات مقسمة حسب الأجنحة لتسهيل المطابقة الرياضية
    # الترتيب داخلياً: P1_carried(احمر, وردي, ابيض), P2_carried(احمر, اصفر), P3_carried(ارجواني, وردي), P4_carried(ذهبي, وردي_فاتح)
    p1_carried = Field(tuple, default=(0, 0, 0))
    p2_carried = Field(tuple, default=(0, 0))
    p3_carried = Field(tuple, default=(0, 0))
    p4_carried = Field(tuple, default=(0, 0))
    
    # الاحتياجات المتبقية لكل جناح في هذه العقدة (تتناقص عند التفريغ)
    p1_needs = Field(tuple, mandatory=True)  # جناح 1 (جوري): (أحمر, وردي, أبيض) -> ابتدائي (2, 1, 1)
    p2_needs = Field(tuple, mandatory=True)  # جناح 2 (توليب): (أحمر, أصفر) -> ابتدائي (3, 1)
    p3_needs = Field(tuple, mandatory=True)  # جناح 3 (أوركيد): (أرجواني, وردي) -> ابتدائي (2, 1)
    p4_needs = Field(tuple, mandatory=True)  # جناح 4 (جوليت روز): (ذهبي, وردي فاتح) -> ابتدائي (2, 2)
    
    # مقاييس كلفة خوارزمية A*
    g = Field(int, default=0)                  # الكلفة الفعلية من البداية حتى العقدة n
    h = Field(int, default=0)                  # الكلفة التقديرية (الهيورستيك)
    f = Field(int, default=0)                  # الكلفة الكلية g + h
    
    action = Field(str, default="Initial")     # العملية التي ولدت هذه العقدة (للطباعة والتوثيق)
    status = Field(str, default="open")        # حالة العقدة في شجرة البحث: open, active, closed

class ClosedState(Fact):
    """حقيقة لتخزين الحالات التي تم استكشافها لمنع الحلقات التكرارية (Closed List)"""
    robot_x = Field(int, mandatory=True)
    robot_y = Field(int, mandatory=True)
    p1_needs = Field(tuple, mandatory=True)
    p2_needs = Field(tuple, mandatory=True)
    p3_needs = Field(tuple, mandatory=True)
    p4_needs = Field(tuple, mandatory=True)