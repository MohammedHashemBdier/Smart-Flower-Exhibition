# مشروع: Smart Flower Exhibition — نظام قواعد معرفة (Experta)

## وصف سريع

مشروع عملي بمادة نظم قواعد المعرفة (جامعة دمشق) — محرك قواعد مبني بـ `experta` لحل مسألة توصيل باقات في معرض شبكي باستخدام نهج شبيه بـ A\*، لكن كله ممَثل كـ facts و rules (بدون استخدام `for/while/if/else` في كود الحل النهائي).

## متطلبات

- Python 3.8+ (يفضل استخدام virtual environment)
- الحزمة `experta`

## إعداد بيئة (ويندوز PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install experta
```

(يمكن إضافة `requirements.txt` لاحقًا إذا رغبت)

## تشغيل المشروع

بسيط — يشغّل `main.py` الذي يحمّل الحقائق الابتدائية من قواعد `rules.py` ثم يبدأ البحث:

```powershell
python main.py
```

## تعديل الرقعة والإعدادات

- يوجد ملف `game_config.json` يحتوي مثال الرقعة وإعدادات الجناح، المستودع، وموقع الروبوت.
  لتوليد ملف الحقائق الصريح (`initial_facts.py`) من `game_config.json` استعمل مولد التطوير الموجود في `tools/generate_initial_facts.py`:

```powershell
python tools\generate_initial_facts.py --config game_config.json --out initial_facts.py
```

أضفت سكربت مطور `tools/generate_initial_facts.py` لتوليد `initial_facts.py` من `game_config.json` عند الحاجة. تم نقل سكربتات المساعدة إلى مجلد `tools/` (أدوات تطوير/بناء)، وهي خارج منطق الـ KB النهائي.

## ملاحظات مهمة عن شروط المادة

- ملف الحل النهائي (الكود الذي سيُدرَس ويُقدّم) يجب أن لا يحتوي تعليمات إجرائية مثل `for`, `while`, `if`, `else` في منطق الحل. لذلك قمنا بإحدى الطريقتين:
  - وضع الحقائق الابتدائية كـ `@DefFacts()` داخل `rules.py` (حاليًا مُفعّل)، أو
  - توليد ملف `initial_facts.py` صريح يحتوي `engine.declare(...)` بدون حلقات/شروط.

## ما قمتُ به بالفعل

- نقلت تهيئة الحالة الابتدائية إلى `@DefFacts()` داخل `rules.py` (محرك الخبرة يحمّلها تلقائيًا عند `engine.reset()`).
- أضفت سكربت مطور `scripts/generate_initial_facts.py` لتوليد `initial_facts.py` من `game_config.json` عند الحاجة.

## اقتراحات للخطوات التالية

- إضافة `requirements.txt` لتجميد الحزم (أفعل ذلك إن رغبت).
- إضافة اختبارات: `tests/test_heuristics.py` و`tests/test_run_smoke.py` (أستطيع إضافتها الآن).
- تجهيز ملف تسليم `deliverables.md` + أرشيف ZIP للتسليم.

كيف تريد أن أتابع الآن؟

- أضيف اختبارات (unit + smoke)?
- أجهز `requirements.txt`؟
- أجهز ملف تسليم/قائمة تحقق؟
