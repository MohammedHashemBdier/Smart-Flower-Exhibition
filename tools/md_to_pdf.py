from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import textwrap

import os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
in_path = os.path.join(root, 'deliverables.md')
out_path = os.path.join(root, 'deliverables.pdf')

with open(in_path, 'r', encoding='utf-8') as f:
    text = f.read()

c = canvas.Canvas(out_path, pagesize=A4)
width, height = A4
margin = 40
y = height - margin
lines = text.splitlines()
for paragraph in lines:
    if paragraph.strip() == '':
        y -= 12
        continue
    wrapped = textwrap.wrap(paragraph, width=95)
    for line in wrapped:
        if y < margin + 50:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= 12

c.save()
print('Wrote', out_path)
