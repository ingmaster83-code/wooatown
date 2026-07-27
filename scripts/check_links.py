# -*- coding: utf-8 -*-
"""생성된 모든 지역 페이지의 아웃바운드 링크(카테고리 카드)가 실제로 200을 반환하는지 전수 검사."""
import os
import re
import urllib.request
import urllib.parse

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "지역")

# fonts.googleapis.com은 HEAD 요청 자체를 이상하게 처리하는 게 알려진 문제라 제외,
# wooatown 자기 자신은 아직 배포 전이라 제외 — 실제로 검사할 건 카테고리 카드(target=_blank)만
SKIP_HOSTS = ("fonts.googleapis.com", "wooatown.wooahouse.com")


def encode_url(url):
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


bad = []
checked = 0
for fname in sorted(os.listdir(DOCS)):
    if not fname.endswith(".html"):
        continue
    text = open(os.path.join(DOCS, fname), encoding="utf-8").read()
    cards = re.findall(r'<a href="(https://[^"]+)"[^>]*class="cat-card"', text)
    for url in cards:
        if any(h in url for h in SKIP_HOSTS):
            continue
        checked += 1
        safe_url = encode_url(url)
        try:
            req = urllib.request.Request(safe_url, method="GET", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = f"ERR:{e}"
        if code != 200:
            bad.append((fname, url, code))
            print(f"[FAIL {code}] {fname} -> {url}")

print(f"\n총 {checked}개 링크 검사, 실패 {len(bad)}개")
