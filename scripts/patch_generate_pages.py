#!/usr/bin/env python3
"""generate_pages.py 를 16개 사이트 + 시군구 링크 섹션 지원으로 1회 패치한다."""
import re
from pathlib import Path

p = Path(__file__).parent / "generate_pages.py"
s = p.read_text(encoding="utf-8")

# 1) 사이트 순서/URL 빌더
s = s.replace('''    "hosppass": url_short_지역,
}''', '''    "hosppass": url_short_지역,
    "wooaleisure": url_short_region,
    "wooasnack": url_short_region,
    "wooalotto": url_short_region,
    "wooabroker": url_short_region,
    "wooaconstruct": url_short_region,
    "wooapay": url_short_region,
    "wooahagwon": url_short_region,
}''')
s = s.replace('''SITE_ORDER = ["wooasijang", "wooapet", "wooabike", "wooaparking", "wooacamp",
              "wooakids", "wooaparkgolf", "wooacharge", "hosppass"]''', '''SITE_ORDER = ["wooasijang", "wooapet", "wooabike", "wooaparking", "wooacamp",
              "wooakids", "wooaparkgolf", "wooacharge", "hosppass",
              "wooaleisure", "wooasnack", "wooalotto", "wooabroker", "wooaconstruct", "wooapay", "wooahagwon"]
N_SITES = len(SITE_ORDER)

# 시군구 링크 섹션용 (extract_dong_counts.py 가 만든 캐시가 있으면 사용)
SG_BY_REGION = {}
_cache = os.path.join(BASE, "scripts", "_cache", "dong_hub.json")
if os.path.exists(_cache):
    with open(_cache, encoding="utf-8") as _f:
        _hub = json.load(_f)
    for _v in _hub["sigungu"].values():
        if _v["total"] > 0:
            SG_BY_REGION.setdefault(_v["do"], []).append(_v)
    for _r in SG_BY_REGION:
        SG_BY_REGION[_r].sort(key=lambda v: (-v["total"], v["sg"]))


def sigungu_section(region):
    from urllib.parse import quote
    lst = SG_BY_REGION.get(region, [])
    if not lst:
        return ""
    chips = "".join(
        f'<a class="chip" href="/동네/{quote(v["do"], safe="")}/{quote(v["sgSlug"], safe="")}/">{esc(v["sg"])}<em>{v["total"]:,}</em></a>'
        for v in lst
    )
    return f"""
    <section class="seo-intro">
      <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:12px;">📍 {esc(REGION_FULL[region])} 시군구·동네별 생활정보</h2>
      <div class="chip-row">{chips}</div>
    </section>
"""''')

# 2) '9개' 문구 동적화
s = s.replace("우아하우스 생활정보 9개 사이트 모음", "우아하우스 생활정보 {N_SITES}개 사이트 모음")
s = s.replace("우아하우스 생활정보 사이트 9개를 지역별로 한곳에 모았습니다. 전통시장, 주차장, 캠핑장, 파크골프장, 전기차 충전소, 어린이 놀이시설, 반려동물 동반여행지, 병원·약국까지",
              "우아하우스 생활정보 사이트 {N_SITES}개를 지역별·동네별로 한곳에 모았습니다. 전통시장, 주차장, 캠핑장, 병원·약국, 체육시설, 겨울간식, 복권 판매점, 공인중개사, 학원까지")
s = s.replace("우아하우스 생활정보 사이트 9곳을 지역별로 한곳에 모았어요", "우아하우스 생활정보 사이트 {N_SITES}곳을 지역별·동네별로 한곳에 모았어요")
s = s.replace("우아하우스가 만든 9개의 지역 생활정보 사이트(전통시장, 주차장, 캠핑장, 파크골프장,",
              "우아하우스가 만든 {N_SITES}개의 지역 생활정보 사이트(전통시장, 주차장, 캠핑장, 파크골프장, 체육시설, 겨울간식, 복권 판매점, 공인중개사, 학원, 건설업체, 지역화폐 가맹점,")
s = s.replace("9개 공공데이터 사이트를", "16개 공공데이터 사이트를")

# 3) 시도 페이지에 시군구 섹션 삽입 (카테고리 그리드 뒤, seo-intro 앞)
marker = '''    <section class="seo-intro">
      <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:12px;">{esc(full)} 생활정보 안내</h2>'''
assert marker in s
s = s.replace(marker, "    {sigungu_section(region)}\n" + marker, 1)

# 4) 사이트맵: 동네 사이트맵은 generate_dong_pages 가 이어 쓴다 (기본 사이트맵은 유지)
p.write_text(s, encoding="utf-8")
print("patched; N_SITES 사용 횟수:", s.count("{N_SITES}"))
