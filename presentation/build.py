#!/usr/bin/env python3
"""Inline fonts + Chart.js into a self-contained presentation HTML."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

def read(p):
    with open(os.path.join(HERE, p), 'r', encoding='utf-8') as f:
        return f.read()

tpl = read('template.html')
fonts = read('assets/fonts-embedded.css')
chartjs = read('assets/chart.umd.min.js')

html = tpl.replace('/*__FONTS_CSS__*/', fonts).replace('/*__CHARTJS__*/', chartjs)

out = os.path.join(HERE, 'doma-karkas-presentation.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Built {out}")
print(f"  size = {os.path.getsize(out)/1024:.0f} KB")
print(f"  fonts inlined = {len(fonts)} chars, chart.js inlined = {len(chartjs)} chars")
assert '/*__FONTS_CSS__*/' not in html, "fonts placeholder not replaced"
assert '/*__CHARTJS__*/' not in html, "chartjs placeholder not replaced"
print("  placeholders replaced OK")
