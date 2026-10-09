#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""우아동네 동네(시군구·동) 허브 페이지 생성기.

scripts/_cache/dong_hub.json (extract_dong_counts.py 결과)을 읽어
  docs/동네/{시도}/{시군구슬러그}/index.html          시군구 허브
  docs/동네/{시도}/{시군구슬러그}/{동}/index.html     동 허브
를 만들고 sitemap.xml 을 갱신한다. 콘텐츠를 복제하지 않고 사이트별 개수·링크만 모은다.
"""
import json, os, sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_pages as gp  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
DOCS = gp.DOCS
CACHE = os.path.join(gp.BASE, "scripts", "_cache", "dong_hub.json")
DATA = json.load(open(CACHE, encoding="utf-8"))
SRC = DATA["sources"]
ORDER = ["wooaleisure", "wooasnack", "wooalotto", "wooabroker", "wooaconstruct", "wooapay", "wooahagwon"]
UNIT = {"wooaleisure": "체육시설", "wooasnack": "간식 가게", "wooalotto": "복권 판매점", "wooabroker": "공인중개사사무소",
        "wooaconstruct": "건설업체", "wooapay": "지역화폐 가맹점", "wooahagwon": "학원·교습소"}
SHORT = {"wooaleisure": "체육시설", "wooasnack": "겨울간식", "wooalotto": "복권방", "wooabroker": "중개사",
         "wooaconstruct": "건설업체", "wooapay": "가맹점", "wooahagwon": "학원"}

# 같은 이름의 시군구가 여러 시도에 있는 경우(중구·북구 등)
_names = {}
for v in DATA["sigungu"].values():
    _names.setdefault(v["sg"], set()).add(v["do"])
AMBIG = {sg for sg, ds in _names.items() if len(ds) > 1}


def sg_name(do, sg):
    return f"{do} {sg}" if sg in AMBIG else sg


def q(s):
    return quote(str(s), safe="")


def dong_url(do, sg_slug, dong):
    return f"/동네/{q(do)}/{q(sg_slug)}/{q(dong)}/"


def sg_url(do, sg_slug):
    return f"/동네/{q(do)}/{q(sg_slug)}/"


def top_sources(counts, k=3):
    return sorted(((n, key) for key, n in counts.items() if n > 0), reverse=True)[:k]


def summary_text(do, sg, dong, counts, total):
    rows = top_sources(counts, 7)
    parts = [f"{UNIT[key]} {n:,}곳" for n, key in rows]
    head = f"{do} {sg} {dong}에는 우아하우스 사이트 {len(rows)}곳에 정리된 생활정보가 모두 {total:,}건 있습니다"
    return head + f" ({', '.join(parts[:4])}{' 등' if len(parts) > 4 else ''}). 아래 카드를 누르면 해당 동네의 상세 목록을 전문 사이트에서 볼 수 있습니다."


def card(key, n, url, sub=None):
    m = SRC[key]
    sub_html = f'<span class="cat-desc">{gp.esc(" · ".join(f"{l} {c}" for l, c in sub))}</span>' if sub else f'<span class="cat-desc">{gp.esc(m["desc"])}</span>'
    return f"""
      <a href="{url}" target="_blank" rel="noopener" class="cat-card">
        <span class="cat-icon">{m['icon']}</span>
        <span class="cat-body">
          <span class="cat-name">{gp.esc(m['name'])}</span>
          {sub_html}
        </span>
        <span class="cat-count">{n:,}</span>
      </a>"""


def shell(title, desc, canonical, h1, sub, breadcrumb, body_html, extra_head="", extra_body=""):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{gp.esc(title)} | 우아동네</title>
  <meta name="description" content="{gp.esc(desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://wooatown.wooahouse.com{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{gp.esc(title)} | 우아동네">
  <meta property="og:description" content="{gp.esc(desc)}">
  <meta property="og:url" content="https://wooatown.wooahouse.com{canonical}">
  <meta property="og:image" content="https://wooatown.wooahouse.com/og-image.png">
  <meta name="twitter:card" content="summary">
  {gp.HEAD_STYLE}
  <link rel="stylesheet" href="/css/style.css">
  {extra_head}
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="/" class="site-logo"><span class="logo-icon">🏘️</span><span class="logo-text">우아동네</span></a>
    <nav class="header-nav">
      <a href="/">지역별</a>
      <a href="https://wooahouse.com" target="_blank" rel="noopener">WooaHouse →</a>
    </nav>
  </div>
</header>

<section class="region-hero">
  <nav class="breadcrumb-hero">{breadcrumb}</nav>
  <h1>🏘️ {gp.esc(h1)}</h1>
  <p class="sub">{gp.esc(sub)}</p>
</section>

<div class="tab-bottom-ad">
  <ins class="adsbygoogle" style="display:inline-block;width:728px;max-width:100%;height:90px"
       data-ad-client="ca-pub-6464921081676309" data-ad-slot="7080296704"></ins>
</div>

<div class="main-layout">
  <div class="main-col">
{body_html}
  </div>

  <aside class="sidebar">
    <div class="sidebar-box">
      <h3>💡 우아동네란?</h3>
      <ul>
        <li>🏘️ 우아하우스 생활정보 {gp.N_SITES}개 사이트 모음</li>
        <li>📍 시도·시군구·동네별로 한눈에</li>
        <li>🔗 클릭하면 전문 사이트로 이동</li>
      </ul>
    </div>
    <div class="sidebar-ad">
      <ins class="adsbygoogle" style="display:inline-block;width:300px;height:600px"
           data-ad-client="ca-pub-6464921081676309" data-ad-slot="6255378195"></ins>
    </div>
  </aside>
</div>

{gp.COUPANG_HTML}
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-col"><p class="footer-heading">정보</p><a href="/privacy.html">개인정보처리방침</a><a href="/">메인으로</a></div>
    </div>
    <div class="footer-bottom"><p>&copy; 2026 WooaHouse. All rights reserved.</p></div>
{gp.COUPANG_DISCLOSURE}  </div>
</footer>
{extra_body}
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6464921081676309" crossorigin="anonymous"></script>
<script>document.querySelectorAll('ins.adsbygoogle').forEach(function(){{(adsbygoogle=window.adsbygoogle||[]).push({{}});}});</script>
</body>
</html>"""


def faq_block(pairs):
    items = "".join(f"<details><summary>{gp.esc(q_)}</summary><p>{gp.esc(a)}</p></details>" for q_, a in pairs)
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                     "mainEntity": [{"@type": "Question", "name": q_, "acceptedAnswer": {"@type": "Answer", "text": a}} for q_, a in pairs]}, ensure_ascii=False)
    return f'<section class="faq-block"><h2>자주 묻는 질문</h2>{items}</section>\n<script type="application/ld+json">{ld}</script>'


def dong_page(v, prev_d, next_d):
    do, sg, dong, slug = v["do"], v["sg"], v["dong"], v["sgSlug"]
    sgn = sg_name(do, sg)
    counts = v["counts"]
    total = v["total"]
    tops = top_sources(counts, 3)
    top_txt = "·".join(SHORT[key] for _n, key in tops)
    title = f"{sgn} {dong} 생활정보 - {top_txt} {total:,}건"
    summary = summary_text(do, sg, dong, counts, total)
    cards = "".join(card(key, counts[key], v["links"][key], v["sub"].get(key)) for _n, key in top_sources(counts, 7))
    near = v.get("near", [])
    near_chips = "".join(
        f'<a class="chip" href="{dong_url(n[0], n[2], n[3])}">{gp.esc(n[3])}<em>{n[5]:,}</em></a>' for n in near[:8])
    near_html = f'<section class="seo-intro"><h2 style="font-size:1.05rem;font-weight:700;margin-bottom:10px;">📍 이웃 동네 생활정보</h2><div class="chip-row">{near_chips}</div></section>' if near_chips else ""
    near_names = ", ".join(f"{n[3]}({n[4]}km)" for n in near[:4])
    pairs = [
        (f"{dong}에는 어떤 생활정보가 있나요?",
         f"{do} {sg} {dong}에는 " + ", ".join(f"{UNIT[key]} {n:,}곳" for n, key in top_sources(counts, 7)) + "이 정리되어 있습니다."),
    ]
    if near_names:
        pairs.append((f"{dong} 근처 동네는 어디인가요?", f"가까운 동네는 {near_names} 순입니다."))
    faq = faq_block(pairs)
    sg_link = f'<a href="{sg_url(do, slug)}">{gp.esc(sgn)} 동네별 생활정보 →</a>'
    nav = f'<div class="dong-nav"><a href="{dong_url(do, slug, prev_d)}">← {gp.esc(prev_d)}</a><a href="{dong_url(do, slug, next_d)}">{gp.esc(next_d)} →</a></div>'
    body = f"""
    <p class="summary-p">{gp.esc(summary)}</p>
    <div class="cat-grid-wrap" style="padding:0;">
      <div class="cat-grid">
        {cards}
      </div>
    </div>
    {near_html}
    {nav}
    {faq}
    <section class="seo-intro">
      <h2 style="font-size:1.05rem;font-weight:700;margin-bottom:10px;">{gp.esc(dong)} 생활정보 안내</h2>
      <p style="color:var(--text-muted);font-size:.88rem;line-height:1.8;">
        {gp.esc(do)} {gp.esc(sg)} {gp.esc(dong)}의 체육시설, 겨울간식 가게, 복권 판매점, 공인중개사, 건설업체, 지역화폐 가맹점, 학원 정보를 우아하우스 전문 사이트에서 모아 개수로 보여드립니다.
        각 카드를 누르면 해당 동네의 상세 목록과 주소·전화번호를 볼 수 있습니다. 공공 인허가 데이터 기준이라 폐업·이전이 늦게 반영될 수 있으니 방문 전에 확인하세요.
      </p>
      <p style="margin-top:10px;font-size:.9rem;">{sg_link} · <a href="/지역/{q(do)}.html">{gp.esc(gp.REGION_FULL[do])} 생활정보 →</a></p>
    </section>"""
    bc = f'<a href="/">홈</a> <span>›</span> <a href="/지역/{q(do)}.html">{gp.esc(do)}</a> <span>›</span> <a href="{sg_url(do, slug)}">{gp.esc(sg)}</a> <span>›</span> <span>{gp.esc(dong)}</span>'
    css_extra = ""
    desc = f"{do} {sg} {dong}의 " + "·".join(UNIT[key] for _n, key in top_sources(counts, 4)) + f" 등 생활정보 {total:,}건. 동네별로 한눈에 확인하고 전문 사이트에서 상세 목록을 보세요."
    return shell(title, desc, dong_url(do, slug, dong), f"{sgn} {dong} 생활정보", f"{do} {sg} {dong} · 총 {total:,}건 · 우아하우스 사이트 {len(counts)}곳 정리", bc, body, css_extra)


def sigungu_page(v):
    do, sg, slug = v["do"], v["sg"], v["sgSlug"]
    sgn = sg_name(do, sg)
    counts = v["counts"]
    total = v["total"]
    cards = "".join(card(key, counts[key], v["links"][key]) for _n, key in top_sources(counts, 7))
    chips = "".join(f'<a class="chip" href="{dong_url(do, slug, d)}">{gp.esc(d)}<em>{t:,}</em></a>' for d, t in v["dongs"])
    tops = top_sources(counts, 3)
    top_txt = "·".join(SHORT[key] for _n, key in tops)
    title = f"{sgn} 생활정보 - {top_txt} {total:,}건, 동네별 보기"
    summary = f"{do} {sg}에는 우아하우스가 정리한 생활정보가 모두 {total:,}건 있고, {len(v['dongs'])}개 동네별로 나눠 볼 수 있습니다 (" + ", ".join(f"{UNIT[key]} {n:,}곳" for n, key in top_sources(counts, 4)) + ")."
    body = f"""
    <p class="summary-p">{gp.esc(summary)}</p>
    <div class="cat-grid-wrap" style="padding:0;">
      <div class="cat-grid">
        {cards}
      </div>
    </div>
    <section class="seo-intro">
      <h2 style="font-size:1.05rem;font-weight:700;margin-bottom:10px;">📍 {gp.esc(sg)} 동네별 생활정보</h2>
      <div class="chip-row">{chips}</div>
    </section>
    <section class="seo-intro">
      <p style="color:var(--text-muted);font-size:.88rem;line-height:1.8;">{gp.esc(do)} {gp.esc(sg)}의 동네 이름을 눌러 체육시설·겨울간식·복권 판매점·공인중개사·건설업체·학원 정보를 한눈에 확인하세요. 집계는 동네 단위로 확인된 업체 기준입니다.</p>
      <p style="margin-top:10px;font-size:.9rem;"><a href="/지역/{q(do)}.html">{gp.esc(gp.REGION_FULL[do])} 생활정보 →</a></p>
    </section>"""
    bc = f'<a href="/">홈</a> <span>›</span> <a href="/지역/{q(do)}.html">{gp.esc(do)}</a> <span>›</span> <span>{gp.esc(sg)}</span>'
    desc = f"{do} {sg}의 체육시설·겨울간식·복권방·공인중개사·건설업체·학원 등 생활정보 {total:,}건을 {len(v['dongs'])}개 동네별로 모았습니다."
    return shell(title, desc, sg_url(do, slug), f"{sgn} 생활정보", f"{do} {sg} · 총 {total:,}건 · 동네 {len(v['dongs'])}곳", bc, body)


def main():
    n_sg = n_dong = 0
    urls = []
    by_sg = {}
    for key, v in DATA["dongs"].items():
        by_sg.setdefault((v["do"], v["sg"]), []).append(v)
    for (do, sg), lst in by_sg.items():
        lst.sort(key=lambda x: x["dong"])
    for skey, sv in DATA["sigungu"].items():
        do, sg, slug = sv["do"], sv["sg"], sv["sgSlug"]
        lst = by_sg.get((do, sg), [])
        if not lst:
            continue
        d = os.path.join(DOCS, "동네", do, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(sigungu_page(sv))
        urls.append(f"https://wooatown.wooahouse.com{sg_url(do, slug)}")
        n_sg += 1
        for i, v in enumerate(lst):
            prev_d = lst[(i - 1) % len(lst)]["dong"]
            next_d = lst[(i + 1) % len(lst)]["dong"]
            dd = os.path.join(d, v["dong"])
            os.makedirs(dd, exist_ok=True)
            open(os.path.join(dd, "index.html"), "w", encoding="utf-8").write(dong_page(v, prev_d, next_d))
            urls.append(f"https://wooatown.wooahouse.com{dong_url(do, slug, v['dong'])}")
            n_dong += 1

    base_urls = ["https://wooatown.wooahouse.com/"] + [f"https://wooatown.wooahouse.com/지역/{r}.html" for r in gp.CANON]
    allu = base_urls + urls
    CH = 40000
    chunks = [allu[i:i + CH] for i in range(0, len(allu), CH)]
    for old in os.listdir(DOCS):
        if old.startswith("sitemap-") and old.endswith(".xml"):
            os.remove(os.path.join(DOCS, old))
    if len(chunks) == 1:
        body = "\n".join(f"  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.6</priority></url>" for u in allu)
        open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8").write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")
    else:
        for i, c in enumerate(chunks, 1):
            body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in c)
            open(os.path.join(DOCS, f"sitemap-{i}.xml"), "w", encoding="utf-8").write(
                '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")
        idx = "\n".join(f"  <sitemap><loc>https://wooatown.wooahouse.com/sitemap-{i}.xml</loc></sitemap>" for i in range(1, len(chunks) + 1))
        open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8").write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + idx + "\n</sitemapindex>\n")
    print(f"시군구 {n_sg}개, 동 {n_dong}개 생성, 사이트맵 URL {len(allu):,}개")


if __name__ == "__main__":
    main()
