# -*- coding: utf-8 -*-
"""9개 공공데이터 사이트에서 시도별 개수를 뽑아 docs/hub_data.json 으로 통합.
각 사이트마다 원본 데이터 형식/지역명 표기가 달라서 사이트별 어댑터 함수를 둔다."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "hub_data.json")

CANON = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
         "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

VARIANT_TO_CANON = {
    "강원특별자치도": "강원", "강원도": "강원", "강원": "강원",
    "경기도": "경기", "경기": "경기",
    "경상남도": "경남", "경남": "경남",
    "경상북도": "경북", "경북": "경북",
    "광주광역시": "광주", "광주": "광주",
    "대구광역시": "대구", "대구": "대구",
    "대전광역시": "대전", "대전": "대전",
    "부산광역시": "부산", "부산": "부산",
    "서울특별시": "서울", "서울": "서울",
    "세종특별자치시": "세종", "세종시": "세종", "세종": "세종",
    "울산광역시": "울산", "울산": "울산",
    "인천광역시": "인천", "인천": "인천",
    "전라남도": "전남", "전남": "전남",
    "전라북도": "전북", "전북특별자치도": "전북", "전북": "전북",
    "제주특별자치도": "제주", "제주도": "제주", "제주": "제주",
    "충청남도": "충남", "충남": "충남",
    "충청북도": "충북", "충북": "충북",
}


def norm(raw):
    if not raw:
        return None
    return VARIANT_TO_CANON.get(str(raw).strip())


def empty_counts():
    return {c: 0 for c in CANON}


def p(*parts):
    return os.path.join(ROOT, *parts)


# ── 1. 우아시장 ──────────────────────────────────
def extract_wooasijang():
    counts = empty_counts()
    data = json.load(open(p("wooasijang", "_data", "markets.json"), encoding="utf-8"))
    for m in data:
        c = norm(m.get("region"))
        if c:
            counts[c] += 1
    return counts


# ── 2. 우아펫 ────────────────────────────────────
def extract_wooapet():
    counts = empty_counts()
    data = json.load(open(p("wooapet", "docs", "pets.json"), encoding="utf-8"))
    for m in data:
        c = norm(m.get("region"))
        if c:
            counts[c] += 1
    return counts


# ── 3. 우아자전거 ────────────────────────────────
KNOWN_REGION_PREFIXES = sorted(VARIANT_TO_CANON.keys(), key=len, reverse=True)


def region_from_addr(addr):
    for prefix in KNOWN_REGION_PREFIXES:
        if addr.startswith(prefix):
            return VARIANT_TO_CANON[prefix]
    return None


def extract_wooabike():
    counts = empty_counts()
    data = json.load(open(p("wooabike", "scripts", "_bike_raw.json"), encoding="utf-8"))
    for it in data:
        addr = it.get("rdnmadr") or it.get("lnmadr") or ""
        c = region_from_addr(addr)
        if c:
            counts[c] += 1
    return counts


# ── 4. 우아파킹 ──────────────────────────────────
def extract_wooaparking():
    counts = empty_counts()
    d = p("wooaparking", "docs", "data", "parking")
    for fname in os.listdir(d):
        if not fname.endswith(".json"):
            continue
        region_name = fname[:-5]
        c = norm(region_name)
        if not c:
            continue
        data = json.load(open(os.path.join(d, fname), encoding="utf-8"))
        records = data.get("records", []) if isinstance(data, dict) else data
        # 파일명이 지역명과 정확히 일치하는 진짜 시도 파일만 채택 (오타/시군구 파일은 건수가 극소수라 자연히 걸러짐)
        if len(records) > 50:
            counts[c] = counts.get(c, 0) + len(records)
    return counts


# ── 5. 우아캠프 ──────────────────────────────────
def extract_wooacamp():
    counts = empty_counts()
    data = json.load(open(p("wooacamp", "_rawdata", "camps.json"), encoding="utf-8"))
    for it in data:
        c = norm(it.get("doNm"))
        if c:
            counts[c] += 1
    return counts


# ── 6. 우아키즈 ──────────────────────────────────
def extract_wooakids():
    counts = empty_counts()
    for fname in ["attractions.json", "playgrounds.json"]:
        fp = p("wooakids", "_rawdata", fname)
        if not os.path.exists(fp):
            continue
        data = json.load(open(fp, encoding="utf-8"))
        for it in data:
            c = norm(it.get("sido"))
            if c:
                counts[c] += 1
    return counts


# ── 7. 우아파크골프 ──────────────────────────────
def extract_wooaparkgolf():
    counts = empty_counts()
    data = json.load(open(p("wooaparkgolf", "_rawdata", "parkgolf.json"), encoding="utf-8"))
    for it in data:
        c = norm(it.get("doNm"))
        if c:
            counts[c] += 1
    return counts


# ── 8. 우아충전소 ────────────────────────────────
def extract_wooacharge():
    counts = empty_counts()
    data = json.load(open(p("wooacharge", "_data", "regions.json"), encoding="utf-8"))
    for it in data:
        c = norm(it.get("sido"))
        if c:
            counts[c] += it.get("total", 0)
    return counts


# ── 9. hosppass (병원/약국) ──────────────────────
def extract_hosppass():
    counts = empty_counts()
    d = p("hosppass", "data", "regions")
    for fname in os.listdir(d):
        if not fname.endswith(".json"):
            continue
        data = json.load(open(os.path.join(d, fname), encoding="utf-8"))
        c = norm(data.get("sido_nm"))
        if not c:
            continue
        counts[c] += len(data.get("hospitals", [])) + len(data.get("pharmacies", []))
    return counts


SITES = {
    "wooasijang": {
        "name": "우아시장", "icon": "🏪", "desc": "전국 전통시장 장날 정보",
        "domain": "wooasijang.wooahouse.com",
        "extract": extract_wooasijang,
    },
    "wooapet": {
        "name": "우아펫", "icon": "🐾", "desc": "반려동물 동반여행지",
        "domain": "wooapet.wooahouse.com",
        "extract": extract_wooapet,
    },
    "wooabike": {
        "name": "우아자전거", "icon": "🚲", "desc": "공공자전거 대여소",
        "domain": "wooabike.wooahouse.com",
        "extract": extract_wooabike,
    },
    "wooaparking": {
        "name": "우아파킹", "icon": "🅿️", "desc": "공영주차장",
        "domain": "wooaparking.wooahouse.com",
        "extract": extract_wooaparking,
    },
    "wooacamp": {
        "name": "우아캠프", "icon": "⛺", "desc": "전국 캠핑장",
        "domain": "wooacamp.wooahouse.com",
        "extract": extract_wooacamp,
    },
    "wooakids": {
        "name": "우아키즈", "icon": "🧸", "desc": "어린이 놀이시설",
        "domain": "wooakids.wooahouse.com",
        "extract": extract_wooakids,
    },
    "wooaparkgolf": {
        "name": "우아파크골프", "icon": "⛳", "desc": "전국 파크골프장",
        "domain": "wooaparkgolf.wooahouse.com",
        "extract": extract_wooaparkgolf,
    },
    "wooacharge": {
        "name": "우아충전소", "icon": "🔌", "desc": "전기차 충전소",
        "domain": "wooacharge.wooahouse.com",
        "extract": extract_wooacharge,
    },
    "hosppass": {
        "name": "우아병원", "icon": "🏥", "desc": "병원·약국 찾기",
        "domain": "hosppass.wooahouse.com",
        "extract": extract_hosppass,
    },
}


def main():
    result = {}
    for key, meta in SITES.items():
        try:
            counts = meta["extract"]()
            total = sum(counts.values())
            result[key] = {
                "name": meta["name"], "icon": meta["icon"], "desc": meta["desc"],
                "domain": meta["domain"], "counts": counts, "total": total,
            }
            print(f"{meta['name']}: 총 {total}건")
        except Exception as e:
            print(f"[실패] {meta['name']}: {e}")
            raise

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n저장 완료: {OUT}")


if __name__ == "__main__":
    main()
