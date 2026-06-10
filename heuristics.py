def pavilion_total(needs):
    return sum(needs)

def distance_score(robot_x, robot_y, pavilion_x, pavilion_y, needs):
    return abs(robot_x - pavilion_x) + abs(robot_y - pavilion_y) + (9999 * int(sum(needs) == 0))

def min4(first, second, third, fourth):
    return min(min(first, second), min(third, fourth))

def calculate_h(robot_x, robot_y, p1_needs, p2_needs, p3_needs, p4_needs):
    total_remaining_bouquets = pavilion_total(p1_needs) + pavilion_total(p2_needs) + pavilion_total(p3_needs) + pavilion_total(p4_needs)
    d1 = distance_score(robot_x, robot_y, 4, 2, p1_needs)
    d2 = distance_score(robot_x, robot_y, 3, 4, p2_needs)
    d3 = distance_score(robot_x, robot_y, 5, 4, p3_needs)
    d4 = distance_score(robot_x, robot_y, 2, 5, p4_needs)
    return total_remaining_bouquets + min4(d1, d2, d3, d4)

def all_needs_zero(p1_needs, p2_needs, p3_needs, p4_needs):
    return (sum(p1_needs) + sum(p2_needs) + sum(p3_needs) + sum(p4_needs)) == 0

def has_invalid_coordinates(robot_x, robot_y, max_x, max_y):
    return (robot_x < 0) or (robot_y < 0) or (robot_x > max_x) or (robot_y > max_y)

def carried_total(carried_load):
    if not carried_load:
        return 0
    # إذا كان الحمولة مختلطة (قائمة من tuples)
    if isinstance(carried_load[0], tuple):
        return sum(qty for _, _, qty in carried_load)
    # الحمولة القديمة (tuple بسيط)
    return sum(carried_load)

def best_pavilion_id(robot_x, robot_y, p1_needs, p2_needs, p3_needs, p4_needs):
    candidates = [
        (distance_score(robot_x, robot_y, 4, 2, p1_needs), 1),
        (distance_score(robot_x, robot_y, 3, 4, p2_needs), 2),
        (distance_score(robot_x, robot_y, 5, 4, p3_needs), 3),
        (distance_score(robot_x, robot_y, 2, 5, p4_needs), 4),
    ]
    return min(candidates)[1]

# دوال جديدة لدعم الحمولة المختلطة (خالية من الحلقات في القواعد، تستخدم فقط هنا)
def is_same_color_load(load, max_load):
    if not load:
        return False
    # load: list of (type_id, color_idx, qty)
    if len(load) == 0:
        return False
    color = load[0][1]
    total_qty = 0
    for _, c, q in load:
        if c != color:
            return False
        total_qty += q
    return total_qty <= max_load and total_qty > 0

def is_same_type_load(load, max_load):
    if not load:
        return False
    typ = load[0][0]
    total_qty = 0
    for t, _, q in load:
        if t != typ:
            return False
        total_qty += q
    return total_qty <= max_load and total_qty > 0

def generate_same_color_loads(max_load):
    # هذه الدالة تستخدم حلقات لأنها خارج القواعد، وهي مولدة للاحتمالات الثابتة
    # ولكن نتيجتها تستخدم فقط في قاعدة واحدة عبر TEST، دون حلقات داخل القاعدة.
    colors = [0,1,2,3,4,5,6]  # 0:أحمر,1:وردي,2:أبيض,3:أصفر,4:أرجواني,5:ذهبي,6:وردي فاتح
    types = [1,2,3,4]         # 1:Rose,2:Tulip,3:Orchid,4:Goliat
    loads = []
    for color in colors:
        for qty in range(1, max_load+1):
            comb = []
            remaining = qty
            for t in types:
                if remaining <= 0:
                    break
                take = min(remaining, 2)  # حد أقصى 2 من كل نوع لتجنب انفجار الحالات
                if take > 0:
                    comb.append((t, color, take))
                    remaining -= take
            if remaining == 0 and comb:
                loads.append(tuple(comb))
    return loads

SAME_COLOR_LOADS = generate_same_color_loads(4)

def is_valid_mixed_load(load, max_load):
    if not load:
        return True
    if is_same_type_load(load, max_load):
        return True
    if is_same_color_load(load, max_load):
        return True
    return False

def deduct_load_from_needs(load, pavilion_needs, pavilion_type):
    # load: tuple of (type_id, color_idx, qty)
    # pavilion_needs: tuple of (need_red, need_pink, need_white, need_yellow, need_purple, need_gold, need_lightpink)
    # نحتاج فقط للألوان المطلوبة حسب نوع الجناح
    # تبسيطاً: نستخدم فقط الألوان التي تهم الجناح (حسب النوع)
    # لكن سنقوم بخصم عام:
    needs_list = list(pavilion_needs)
    new_load = []
    for t, col, qty in load:
        if t == pavilion_type:
            # نفس النوع، يمكن التفريغ
            if col < len(needs_list):
                taken = min(qty, needs_list[col])
                needs_list[col] -= taken
                if qty - taken > 0:
                    new_load.append((t, col, qty - taken))
            else:
                new_load.append((t, col, qty))
        else:
            new_load.append((t, col, qty))
    return tuple(new_load), tuple(needs_list)

def pavilion_total(needs):
    """عدد الباقات المتبقية في مجموعة احتياجات واحدة."""

    return sum(needs)


def distance_score(robot_x, robot_y, pavilion_x, pavilion_y, needs):
    """كلفة تقريبية للوصول إلى جناح واحد مع تجاهل الأجنحة المنجزة."""

    # Pavilion with no needs gets a very large score so unfinished pavilions stay preferred.
    return abs(robot_x - pavilion_x) + abs(robot_y - pavilion_y) + (9999 * int(sum(needs) == 0))


def min4(first, second, third, fourth):
    """أصغر قيمة بين أربع قيم من دون حلقات أو شروط إجرائية."""

    return min(min(first, second), min(third, fourth))


def calculate_h(robot_x, robot_y, p1_needs, p2_needs, p3_needs, p4_needs):
    """هيورستك بسيط ومبرر: احتياجات متبقية + أقرب جناح غير منجز."""

    total_remaining_bouquets = pavilion_total(p1_needs) + pavilion_total(p2_needs) + pavilion_total(p3_needs) + pavilion_total(p4_needs)
    d1 = distance_score(robot_x, robot_y, 4, 2, p1_needs)
    d2 = distance_score(robot_x, robot_y, 3, 4, p2_needs)
    d3 = distance_score(robot_x, robot_y, 5, 4, p3_needs)
    d4 = distance_score(robot_x, robot_y, 2, 5, p4_needs)
    return total_remaining_bouquets + min4(d1, d2, d3, d4)


def all_needs_zero(p1_needs, p2_needs, p3_needs, p4_needs):
    """التحقق من نهاية البحث."""

    return (sum(p1_needs) + sum(p2_needs) + sum(p3_needs) + sum(p4_needs)) == 0


def has_invalid_coordinates(robot_x, robot_y, max_x, max_y):
    """التحقق من خروج الروبوت عن الشبكة."""

    return (robot_x < 0) or (robot_y < 0) or (robot_x > max_x) or (robot_y > max_y)


def carried_total(carried_load):
    """عدد الباقات المحمولة حالياً."""

    return sum(carried_load) * int(bool(carried_load))


def best_pavilion_id(robot_x, robot_y, p1_needs, p2_needs, p3_needs, p4_needs):
    """اختيار الجناح الأقرب كمرشح أول للتحميل."""

    candidates = [
        (distance_score(robot_x, robot_y, 4, 2, p1_needs), 1),
        (distance_score(robot_x, robot_y, 3, 4, p2_needs), 2),
        (distance_score(robot_x, robot_y, 5, 4, p3_needs), 3),
        (distance_score(robot_x, robot_y, 2, 5, p4_needs), 4),
    ]
    return min(candidates)[1]

def _generate_all_same_color_loads(max_load):
    # هذه الدالة تستخدم حلقات ولكنها تُستدعى مرة واحدة فقط عند تحميل الملف
    # النتيجة هي قائمة ثابتة من الحمولات الممكنة
    colors = range(7)  # 0:أحمر,1:وردي,2:أبيض,3:أصفر,4:أرجواني,5:ذهبي,6:وردي فاتح
    types = [1,2,3,4]  # 1:Rose,2:Tulip,3:Orchid,4:Goliat
    all_loads = []
    for color in colors:
        for qty in range(1, max_load+1):
            # نحاول توزيع qty على الأنواع الأربعة بحد أقصى 2 لكل نوع (لتجنب الانفجار)
            # سنقوم بإنشاء جميع التركيبات الممكنة التي لا يتجاوز مجموعها max_load
            # لكن لضمان البساطة، سنقوم بإنشاء تركيبة واحدة فقط لكل لون وكمية (الأولى)
            # إذا أردت جميع التركيبات، ستحتاج إلى recursion ولكن خارج القواعد.
            # هنا سنقوم بطريقة مبسطة لكنها تغطي المثال: نأخذ من كل نوع الحد الأدنى الممكن
            remaining = qty
            comb = []
            for t in types:
                if remaining <= 0:
                    break
                take = min(remaining, 2)
                if take > 0:
                    comb.append((t, color, take))
                remaining -= take
            if remaining == 0 and comb:
                all_loads.append(tuple(comb))
    return all_loads

ALL_SAME_COLOR_LOADS = _generate_all_same_color_loads(4)