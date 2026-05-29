def calculate_h(robot_x, robot_y, p1_needs, p2_needs, p3_needs, p4_needs):
    """
    حساب القيمة الاستكشافية h(n) بشكل ذكي ونقي (بدون أي حلقة تكرارية أو شرط إجرائي)
    الهيورستيك يعتمد على إجمالي عدد الباقات المتبقية المطلوب توصيلها للأجنحة كافة.
    """
    # حساب مجموع الباقات المتبقية في كل جناح باستخدام التابع الوظيفي sum
    total_remaining_bouquets = sum(p1_needs) + sum(p2_needs) + sum(p3_needs) + sum(p4_needs)
    
    # نضرب عدد الباقات المتبقية في كلفة تقديرية خفيفة لضمان تماشيها مع دالة الكلفة
    return total_remaining_bouquets * 2