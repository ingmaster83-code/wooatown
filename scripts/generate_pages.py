#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""우아동네(wooatown) 페이지 생성기 — 16개 공공데이터 사이트를 지역별로 묶어 보여주는 허브.
콘텐츠를 복제하지 않고, 카테고리별 요약(개수)만 보여준 뒤 각 사이트의 실제 지역 페이지로 링크한다."""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "docs")
DATA_PATH = os.path.join(DOCS, "hub_data.json")

CANON = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
         "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

REGION_FULL = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시", "인천": "인천광역시",
    "광주": "광주광역시", "대전": "대전광역시", "울산": "울산광역시", "세종": "세종특별자치시",
    "경기": "경기도", "강원": "강원도", "충북": "충청북도", "충남": "충청남도",
    "전북": "전라북도", "전남": "전라남도", "경북": "경상북도", "경남": "경상남도", "제주": "제주도",
}
# 강원/전북/제주는 최근 "특별자치도"로 개칭 — 새 표기를 쓰는 사이트용
REGION_FULL_NEW = dict(REGION_FULL, 강원="강원특별자치도", 전북="전북특별자치도", 제주="제주특별자치도")

# 우아시장은 광역시는 접미사 없이, 도 단위만 접미사 있는 자체 표기 + 영문 슬러그를 씀
WOOASIJANG_NAME = dict(REGION_FULL, 서울="서울", 부산="부산", 대구="대구", 인천="인천",
                        광주="광주", 대전="대전", 울산="울산", 세종="세종", 제주="제주도")
WOOASIJANG_SLUG = {
    "경기도": "gyeonggi", "인천": "incheon", "강원도": "gangwon", "충청북도": "chungbuk",
    "충청남도": "chungnam", "전라북도": "jeonbuk", "전라남도": "jeonnam", "경상북도": "gyeongbuk",
    "경상남도": "gyeongnam", "대구": "daegu", "울산": "ulsan", "부산": "busan",
    "광주": "gwangju", "세종": "sejong", "대전": "daejeon", "제주도": "jeju", "서울": "seoul",
}



# 쿠팡 파트너스 (고객 관심 기반 추천) — 콘텐츠·애드센스 아래, 페이지 최하단. 고지 문구는 푸터에 표기.
COUPANG_HTML = '''
<div class="coupang-partners" style="margin:36px auto 0;max-width:720px;padding:0 16px 8px;text-align:center;overflow-x:auto;">
  <script src="https://ads-partners.coupang.com/g.js"></script>
  <script>
    new PartnersCoupang.G({"id":980427,"trackingCode":"AF5600192","subId":"town","template":"carousel","width":"680","height":"140"});
  </script>
</div>
'''
COUPANG_DISCLOSURE = '    <p style="margin:6px 0 0;font-size:.7rem;opacity:.55;">이 페이지는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>\n'

def url_wooasijang(region, domain):
    name = WOOASIJANG_NAME[region]
    slug = WOOASIJANG_SLUG[name]
    return f"https://{domain}/region/{slug}/"


def url_full_old_지역(region, domain):
    return f"https://{domain}/지역/{REGION_FULL[region]}.html"


def url_full_new_지역(region, domain):
    return f"https://{domain}/지역/{REGION_FULL_NEW[region]}.html"


def url_full_new_region(region, domain):
    return f"https://{domain}/region/{REGION_FULL_NEW[region]}/"


def url_short_region(region, domain):
    return f"https://{domain}/region/{region}/"


def url_short_지역(region, domain):
    # hosppass는 세종만 "세종시"로 표기하며, 시군구가 없는 단일 행정구역이라
    # index.html 없이 세종시.html 파일 하나만 존재함 (다른 지역과 다른 예외 케이스)
    if region == "세종":
        return f"https://{domain}/지역/세종시/세종시.html"
    return f"https://{domain}/지역/{region}/"


URL_BUILDERS = {
    "wooasijang": url_wooasijang,
    "wooapet": url_full_old_지역,
    "wooabike": url_full_old_지역,
    "wooaparking": url_full_new_지역,
    "wooacamp": url_short_region,
    "wooakids": url_short_region,
    "wooaparkgolf": url_full_new_region,
    "wooacharge": url_full_new_region,
    "hosppass": url_short_지역,
    "wooaleisure": url_short_region,
    "wooasnack": url_short_region,
    "wooalotto": url_short_region,
    "wooabroker": url_short_region,
    "wooaconstruct": url_short_region,
    "wooapay": url_short_region,
    "wooahagwon": url_short_region,
    "wooagym": url_short_region,
    "wooavet": url_short_region,
    "wooakinder": url_short_region,
    "wooasenior": url_short_region,
    "wooagreen": url_short_region,
    "wooaplay": url_short_region,
    "wooashop": url_short_region,
    "wootoilet": url_short_region,
}

with open(DATA_PATH, encoding="utf-8") as f:
    HUB = json.load(f)

SITE_ORDER = ["wooasijang", "wooapet", "wooabike", "wooaparking", "wooacamp",
              "wooakids", "wooaparkgolf", "wooacharge", "hosppass",
              "wooagym", "wooavet", "wooakinder", "wooasenior", "wooagreen", "wooaleisure", "wooasnack", "wooalotto", "wooaplay", "wooashop", "wootoilet", "wooabroker", "wooaconstruct", "wooapay", "wooahagwon"]
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
"""

HEAD_STYLE = """<link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap" rel="stylesheet">"""


def esc(s):
    return (s or "").replace("&", "&amp;").replace('"', "&quot;")


def region_total(region):
    return sum(HUB[k]["counts"].get(region, 0) for k in SITE_ORDER)


def category_cards(region, up):
    cards = []
    for key in SITE_ORDER:
        site = HUB[key]
        count = site["counts"].get(region, 0)
        if count == 0:
            continue
        url = URL_BUILDERS[key](region, site["domain"])
        cards.append(f"""
      <a href="{url}" target="_blank" rel="noopener" class="cat-card">
        <span class="cat-icon">{site['icon']}</span>
        <span class="cat-body">
          <span class="cat-name">{esc(site['name'])}</span>
          <span class="cat-desc">{esc(site['desc'])}</span>
        </span>
        <span class="cat-count">{count:,}</span>
      </a>""")
    return "".join(cards)


def region_page(region):
    full = REGION_FULL[region]
    total = region_total(region)
    cards_html = category_cards(region, up="../")
    footer_up = "../"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(full)} 생활정보 모음 — 시장·주차장·캠핑장·병원 | 우아동네</title>
  <meta name="description" content="{esc(full)} 전통시장, 주차장, 캠핑장, 반려동물 동반여행지, 병원·약국 등 생활정보를 한곳에서 모아봤어요. 카테고리를 눌러 자세한 정보를 확인하세요.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://wooatown.wooahouse.com/지역/{esc(region)}.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(full)} 생활정보 모음 | 우아동네">
  <meta property="og:description" content="{esc(full)} 시장·주차장·캠핑장·병원 등 생활정보 총정리">
  <meta property="og:url" content="https://wooatown.wooahouse.com/지역/{esc(region)}.html">
  <meta name="twitter:card" content="summary">
  {HEAD_STYLE}
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="../" class="site-logo"><span class="logo-icon">🏘️</span><span class="logo-text">우아동네</span></a>
    <nav class="header-nav">
      <a href="../">지역별</a>
      <a href="https://wooahouse.com" target="_blank" rel="noopener">WooaHouse →</a>
    </nav>
  </div>
</header>

<section class="region-hero">
  <nav class="breadcrumb-hero">
    <a href="../">홈</a> <span>›</span> <span>{esc(full)}</span>
  </nav>
  <h1>🏘️ {esc(full)} 생활정보</h1>
  <p class="sub">총 {total:,}건의 생활정보를 카테고리별로 모아봤어요</p>
</section>

<div class="tab-bottom-ad">
  <ins class="adsbygoogle" style="display:inline-block;width:728px;max-width:100%;height:90px"
       data-ad-client="ca-pub-6464921081676309" data-ad-slot="7080296704"></ins>
</div>

<div class="main-layout">
  <div class="main-col">
    <div class="cat-grid-wrap" style="padding:0;">
      <div class="cat-grid">
        {cards_html}
      </div>
    </div>

    {sigungu_section(region)}
    <section class="seo-intro">
      <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:12px;">{esc(full)} 생활정보 안내</h2>
      <p style="color:var(--text-muted);font-size:.88rem;line-height:1.8;">
        {esc(full)}의 전통시장, 공영주차장, 캠핑장, 파크골프장, 전기차 충전소, 어린이 놀이시설, 반려동물 동반여행지, 병원·약국 정보를
        카테고리별로 모아뒀습니다. 각 카드를 누르면 해당 정보를 전문으로 다루는 우아하우스 사이트로 이동해서 상세 내용을 확인할 수 있습니다.
      </p>
    </section>
  </div>

  <aside class="sidebar">
    <div class="sidebar-box">
      <h3>💡 우아동네란?</h3>
      <ul>
        <li>🏘️ 우아하우스 생활정보 {N_SITES}개 사이트 모음</li>
        <li>📍 지역별로 한눈에 확인</li>
        <li>🔗 클릭하면 전문 사이트로 이동</li>
      </ul>
    </div>
    <div class="sidebar-ad">
      <ins class="adsbygoogle" style="display:inline-block;width:300px;height:600px"
           data-ad-client="ca-pub-6464921081676309" data-ad-slot="6255378195"></ins>
    </div>
  </aside>
</div>

{COUPANG_HTML}
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-col"><p class="footer-heading">정보</p><a href="{footer_up}privacy.html">개인정보처리방침</a><a href="{footer_up}">메인으로</a></div>
    </div>
    <div class="footer-bottom"><p>&copy; 2026 WooaHouse. All rights reserved.</p></div>
{COUPANG_DISCLOSURE}  </div>
</footer>

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6464921081676309" crossorigin="anonymous"></script>
<script>document.querySelectorAll('ins.adsbygoogle').forEach(function(){{(adsbygoogle=window.adsbygoogle||[]).push({{}});}});</script>
</body>
</html>"""


def index_page():
    cards = []
    for region in CANON:
        total = region_total(region)
        full = REGION_FULL[region]
        cards.append(
            f'<a href="지역/{esc(region)}.html" class="region-card">'
            f'<span class="region-card-name">{esc(full)}</span>'
            f'<span class="region-card-count">{total:,}건</span></a>'
        )
    cards_html = "".join(cards)
    footer_up = "./"

    site_summary = "".join(
        f'<div class="site-summary-item"><span class="ssi-icon">{HUB[k]["icon"]}</span>'
        f'<span class="ssi-name">{esc(HUB[k]["name"])}</span>'
        f'<span class="ssi-count">{HUB[k]["total"]:,}</span></div>'
        for k in SITE_ORDER
    )

    grand_total = sum(HUB[k]["total"] for k in SITE_ORDER)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>우리 동네 생활정보 모음 — 시장·주차장·캠핑장·병원 한눈에 | 우아동네</title>
  <meta name="description" content="우아하우스 생활정보 사이트 {N_SITES}개를 지역별·동네별로 한곳에 모았습니다. 전통시장, 주차장, 캠핑장, 병원·약국, 체육시설, 겨울간식, 복권 판매점, 공인중개사, 학원까지 우리 동네 생활정보를 한눈에 확인하세요.">
  <meta name="keywords" content="우리 동네 생활정보,지역 정보 모음,전통시장,주차장,캠핑장,병원,약국">
  <meta name="robots" content="index, follow">
  <meta name="naver-site-verification" content="ce4f0929c89793556cb3995f35f7212d3e456535" />
  <link rel="canonical" href="https://wooatown.wooahouse.com/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="우리 동네 생활정보 모음 | 우아동네">
  <meta property="og:description" content="시장·주차장·캠핑장·병원 등 지역 생활정보를 한곳에서">
  <meta property="og:url" content="https://wooatown.wooahouse.com/">
  <meta property="og:image" content="https://wooatown.wooahouse.com/og-image.png">
  <meta name="twitter:card" content="summary">
  {HEAD_STYLE}
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="./" class="site-logo"><span class="logo-icon">🏘️</span><span class="logo-text">우아동네</span></a>
    <nav class="header-nav">
      <a href="./" class="active-nav">지역별</a>
      <a href="https://wooahouse.com" target="_blank" rel="noopener">WooaHouse →</a>
    </nav>
  </div>
</header>

<section class="hero">
  <h1>🏘️ 우리 동네 생활정보 모음</h1>
  <p class="sub">우아하우스 생활정보 사이트 {N_SITES}곳을 지역별·동네별로 한곳에 모았어요</p>
</section>

<div class="main-layout">
  <div class="main-col">
    <div class="tab-bottom-ad">
      <ins class="adsbygoogle" style="display:inline-block;width:728px;max-width:100%;height:90px"
           data-ad-client="ca-pub-6464921081676309" data-ad-slot="7080296704"></ins>
    </div>

    <section class="section">
      <h2 class="section-title" style="text-align:center;margin-bottom:20px;">📊 모아둔 정보</h2>
      <div class="site-summary-grid">
        {site_summary}
      </div>
      <p class="grand-total">총 {grand_total:,}건의 생활정보</p>
    </section>

    <section class="section">
      <h2 class="section-title" style="text-align:center;margin-bottom:24px;">📍 지역별로 찾기</h2>
      <div class="region-grid">
        {cards_html}
      </div>
    </section>

    <section class="seo-intro">
      <h2 style="font-size:1.2rem;font-weight:700;margin-bottom:16px;">우아동네 — 우리 동네 생활정보 모음</h2>
      <p style="color:var(--text-muted);font-size:.9rem;line-height:1.9;">
        <strong>우아동네</strong>는 우아하우스가 만든 {N_SITES}개의 지역 생활정보 사이트(전통시장, 주차장, 캠핑장, 파크골프장, 체육시설, 겨울간식, 복권 판매점, 공인중개사, 학원, 건설업체, 지역화폐 가맹점,
        전기차 충전소, 어린이 놀이시설, 반려동물 동반여행지, 병원·약국)를 지역별로 한곳에 모아 보여주는 종합 안내 페이지입니다.
        지역을 선택하면 그 동네의 생활정보를 카테고리별 개수로 한눈에 확인하고, 자세한 내용은 각 전문 사이트에서 바로 확인할 수 있습니다.
      </p>
    </section>
  </div>

  <aside class="sidebar">
    <div class="sidebar-box">
      <h3>💡 우아동네란?</h3>
      <ul>
        <li>🏘️ 우아하우스 생활정보 {N_SITES}개 사이트 모음</li>
        <li>📍 지역별로 한눈에 확인</li>
        <li>🔗 클릭하면 전문 사이트로 이동</li>
      </ul>
    </div>
    <div class="sidebar-ad">
      <ins class="adsbygoogle" style="display:inline-block;width:300px;height:600px"
           data-ad-client="ca-pub-6464921081676309" data-ad-slot="6255378195"></ins>
    </div>
  </aside>
</div>

{COUPANG_HTML}
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-col"><p class="footer-heading">정보</p><a href="{footer_up}privacy.html">개인정보처리방침</a><a href="{footer_up}">메인으로</a></div>
    </div>
    <div class="footer-bottom"><p>&copy; 2026 WooaHouse. All rights reserved.</p></div>
{COUPANG_DISCLOSURE}  </div>
</footer>

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6464921081676309" crossorigin="anonymous"></script>
<script>document.querySelectorAll('ins.adsbygoogle').forEach(function(){{(adsbygoogle=window.adsbygoogle||[]).push({{}});}});</script>
</body>
</html>"""


def write_sitemap():
    urls = ["https://wooatown.wooahouse.com/"]
    for region in CANON:
        urls.append(f"https://wooatown.wooahouse.com/지역/{region}.html")
    entries = "\n".join(
        f"  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>"
        for u in urls
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n'
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def main():
    os.makedirs(os.path.join(DOCS, "지역"), exist_ok=True)

    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page())

    for region in CANON:
        with open(os.path.join(DOCS, "지역", f"{region}.html"), "w", encoding="utf-8") as f:
            f.write(region_page(region))

    write_sitemap()
    print(f"생성 완료: 지역 {len(CANON)}개 페이지 + 홈")


if __name__ == "__main__":
    main()
