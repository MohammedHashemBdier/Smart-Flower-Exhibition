# --- حل مشكلة توافقية مكتبة experta مع إصدارات بايثون الحديثة ---
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping
# -------------------------------------------------------------

from experta import *
from facts import StateNode, GridConfig
from rules import SmartFlowerEngine, NodeCounter, PavilionConfig
from heuristics import calculate_h

if __name__ == "__main__":
    # 1. تهيئة محرك الاستنتاج الخبير لشجرة البحث
    engine = SmartFlowerEngine()
    engine.reset()

    print("🚀 Initializing Smart Flower Exhibition Knowledge-Based System...")
    print("------------------------------------------------------------------")

    # 2. تعريف الإعدادات الثابتة للشبكة والمستودع (تجنب القيم الصلبة - Hardcoding)
    # لنفرض هنا شبكة بحجم 5x5 كمثال، والمستودع يقع في الخلية (0, 0)
    grid_conf = GridConfig(max_x=4, max_y=4, warehouse_x=0, warehouse_y=0)
    engine.declare(grid_conf)

    # 3. تعريف مواقع الأجنحة (Pavilions) الثابتة في المعرض
    engine.declare(PavilionConfig(pavilion_id=1, x=2, y=1)) # جناح 1
    engine.declare(PavilionConfig(pavilion_id=2, x=1, y=3)) # جناح 2
    engine.declare(PavilionConfig(pavilion_id=3, x=3, y=3)) # جناح 3
    engine.declare(PavilionConfig(pavilion_id=4, x=4, y=2)) # جناح 4

    # 4. تهيئة عدّاد المعرفات الفريدة للعقد (بدءاً من القيمة 1 للعقدة الابتدائية)
    engine.declare(NodeCounter(current_id=1))

    # 5. تحديد احتياجات المعرض الابتدائية حسب نص الوظيفة
    p1_initial_needs = (2, 1, 1)  # جناح 1 (جوري): (أحمر, وردي, أبيض)
    p2_initial_needs = (3, 1)     # جناح 2 (توليب): (أحمر, أصفر)
    p3_initial_needs = (2, 1)     # جناح 3 (أوركيد): (أرجواني, وردي)
    p4_initial_needs = (2, 2)     # جناح 4 (جوليت روز): (ذهبي, وردي فاتح)

    # الروبوت يبدأ من موقع المستودع (0, 0) بحمولة فارغة تماماً
    start_x = 0
    start_y = 0

    # حساب قيمة الهيورستيك h(n) الابتدائية بناءً على دالة مانهاتن الذكية
    initial_h = calculate_h(
        start_x, start_y, 
        p1_initial_needs, p2_initial_needs, p3_initial_needs, p4_initial_needs
    )

    # 6. إعلان عقدة الحالة الابتدائية (Initial State Node) في الـ Working Memory
    initial_node = StateNode(
        node_id=0,
        parent_id=-1,  # ليس لها أب لأنها نقطة الانطلاق
        robot_x=start_x,
        robot_y=start_y,
        p1_carried=(0, 0, 0),
        p2_carried=(0, 0),
        p3_carried=(0, 0),
        p4_carried=(0, 0),
        p1_needs=p1_initial_needs,
        p2_needs=p2_initial_needs,
        p3_needs=p3_initial_needs,
        p4_needs=p4_initial_needs,
        g=0,
        h=initial_h,
        f=0 + initial_h,  # الكلفة الكلية f(n) = g(n) + h(n)
        action="Start at Warehouse",
        status="open"     # جاهزة للاستكشاف والتدقيق عبر المحرك
    )
    engine.declare(initial_node)

    print("🎯 Execution Phase: Running A* Search Algorithm via Production Rules...")
    print("------------------------------------------------------------------")
    
    # 7. إطلاق محرك القواعد للبدء بمسح شجرة البحث وإيجاد المسار الأمثل
    engine.run()