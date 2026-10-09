#!/usr/bin/env python3
"""우아동네 스크립트에 헬스장·동물병원·유치원·경로당·공원 5개 소스를 추가하는 1회성 패치."""
from pathlib import Path

base = Path(__file__).parent

p = base / "extract_dong_counts.py"
s = p.read_text(encoding="utf-8")
anchor = '    ("hosppass", "우아병원",'
assert anchor in s
new = '''    ("wooagym", "우아헬스장", "💪", "헬스장·피트니스·체력단련장", "wooagym.wooahouse.com", "wooagym/_rawdata/hub_items.json", True, None),
    ("wooavet", "우아동물병원", "🐾", "동물병원", "wooavet.wooahouse.com", "wooavet/_rawdata/hub_items.json", True, None),
    ("wooakinder", "우아유치원", "🏫", "유치원", "wooakinder.wooahouse.com", "wooakinder/_rawdata/hub_items.json", True, "note"),
    ("wooasenior", "우아경로당", "🏘️", "경로당·마을회관", "wooasenior.wooahouse.com", "wooasenior/_rawdata/hub_items.json", True, "note"),
    ("wooagreen", "우아그린", "🌳", "도시공원·근린공원", "wooagreen.wooahouse.com", "wooagreen/_rawdata/hub_items.json", True, "note"),
'''
if '"wooagym", "우아헬스장"' not in s:
    s = s.replace(anchor, new + anchor, 1)
p.write_text(s, encoding="utf-8")

p = base / "generate_dong_pages.py"
s = p.read_text(encoding="utf-8")
if '"wooagym"' not in s:
    s = s.replace('ORDER = ["wooaleisure",', 'ORDER = ["wooagym", "wooavet", "wooakinder", "wooasenior", "wooagreen", "wooaleisure",', 1)
    s = s.replace('UNIT = {"hosppass": "병원·약국",', 'UNIT = {"wooagym": "헬스장", "wooavet": "동물병원", "wooakinder": "유치원", "wooasenior": "경로당·마을회관", "wooagreen": "공원", "hosppass": "병원·약국",', 1)
    s = s.replace('SHORT = {"hosppass": "병원·약국",', 'SHORT = {"wooagym": "헬스장", "wooavet": "동물병원", "wooakinder": "유치원", "wooasenior": "경로당", "wooagreen": "공원", "hosppass": "병원·약국",', 1)
p.write_text(s, encoding="utf-8")

p = base / "generate_pages.py"
s = p.read_text(encoding="utf-8")
if '"wooagym": url_short_region' not in s:
    s = s.replace('    "wooaplay": url_short_region,', '    "wooagym": url_short_region,\n    "wooavet": url_short_region,\n    "wooakinder": url_short_region,\n    "wooasenior": url_short_region,\n    "wooagreen": url_short_region,\n    "wooaplay": url_short_region,', 1)
    s = s.replace('"wooaleisure", "wooasnack", "wooalotto", "wooaplay", "wooashop", "wootoilet", "wooabroker", "wooaconstruct", "wooapay", "wooahagwon"]',
                  '"wooagym", "wooavet", "wooakinder", "wooasenior", "wooagreen", "wooaleisure", "wooasnack", "wooalotto", "wooaplay", "wooashop", "wootoilet", "wooabroker", "wooaconstruct", "wooapay", "wooahagwon"]', 1)
p.write_text(s, encoding="utf-8")
print("patched")
