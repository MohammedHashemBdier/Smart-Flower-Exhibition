def pavilion_total(needs):
    """عدد الباقات المتبقية في مجموعة احتياجات واحدة."""

    return sum(needs)


def distance_score(robot_x, robot_y, pavilion_x, pavilion_y, needs):
    """كلفة تقريبية للوصول إلى جناح واحد مع تجاهل الأجنحة المنجزة."""

    # If pavilion has no needs, make it very costly to prefer unfinished pavilions
    return abs(robot_x - pavilion_x) + abs(robot_y - pavilion_y) + (9999 * int(sum(needs) == 0))


def min4(first, second, third, fourth):
    """أصغر قيمة بين أربع قيم من دون حلقات أو شروط إجرائية."""

    return min(min(first, second), min(third, fourth))


def calculate_h(robot_x, robot_y, p1_needs, p2_needs, p3_needs, p4_needs):
    """هيورستك بسيط ومبرر: احتياجات متبقية + أقرب جناح غير منجز."""

    total_remaining_bouquets = pavilion_total(p1_needs) + pavilion_total(p2_needs) + pavilion_total(p3_needs) + pavilion_total(p4_needs)
    d1 = distance_score(robot_x, robot_y, 2, 4, p1_needs)
    d2 = distance_score(robot_x, robot_y, 4, 3, p2_needs)
    d3 = distance_score(robot_x, robot_y, 4, 5, p3_needs)
    d4 = distance_score(robot_x, robot_y, 5, 2, p4_needs)
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
        (distance_score(robot_x, robot_y, 2, 4, p1_needs), 1),
        (distance_score(robot_x, robot_y, 4, 3, p2_needs), 2),
        (distance_score(robot_x, robot_y, 4, 5, p3_needs), 3),
        (distance_score(robot_x, robot_y, 5, 2, p4_needs), 4),
    ]
    return min(candidates)[1]