#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""우아동네 동 단위 허브용 데이터 추출.

동 단위 페이지(region/{시도}/{시군구}/{동})가 있는 7개 자매 사이트(레저·간식·복권·중개사·건설·페이·학원)의
시도별 샤드(_rawdata)를 읽어서
  1) docs/hub_data.json 에 7개 사이트의 시도별 개수를 추가하고
  2) scripts/_cache/dong_hub.json 에 동/시군구별 집계(+링크, 근처 동)를 만든다.

동 키 정규화: 구 단위(수원시 영통구)까지 쓰는 레저·간식·복권·중개사를 '기준'으로 삼고,
시 단위(수원시)만 쓰는 건설·페이·학원은 (시도, 시, 동)이 기준 동 하나로만 매핑될 때만 합친다.
"""
import glob, json, math, os, sys
from collections import Counter, defaultdict
from urllib.parse import quote

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)
DOCS = os.path.join(BASE, "docs")
CACHE = os.path.join(BASE, "scripts", "_cache")
os.makedirs(CACHE, exist_ok=True)

CANON = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

# key, 이름, 아이콘, 설명, 도메인, 샤드 glob, 구단위 여부, 세부분류 필드
SOURCES = [
    ("wooaleisure", "우아레저", "🏅", "골프연습장·당구장·태권도장·수영장", "wooaleisure.wooahouse.com", "wooaleisure/_rawdata/lei_*.json", True, "catLabel"),
    ("wooasnack", "우아간식", "🐟", "붕어빵·호떡·토스트 겨울간식 가게", "wooasnack.wooahouse.com", "wooasnack/_rawdata/snk_*.json", True, "typeLabel"),
    ("wooalotto", "우아복권", "🍀", "로또 판매점·1등 당첨점", "wooalotto.wooahouse.com", "wooalotto/_rawdata/lot_*.json", True, None),
    ("wooabroker", "우아중개사", "🏠", "공인중개사사무소", "wooabroker.wooahouse.com", "wooabroker/_rawdata/broker_*.json", True, None),
    ("wooaplay", "우아놀거리", "🎤", "노래방·코인노래방·영화관·공연장", "wooaplay.wooahouse.com", "wooaplay/_rawdata/pl_*.json", True, "catLabel"),
    ("wooashop", "우아가게", "🧺", "빨래방·세탁소·안경점·인쇄소·이발소", "wooashop.wooahouse.com", "wooashop/_rawdata/sh_*.json", True, "catLabel"),
    ("wootoilet", "우아화장실", "🚻", "공중화장실·개방화장실", "wootoilet.wooahouse.com", "wootoilet/_rawdata/tl_*.json", True, "catLabel"),
    ("wooaconstruct", "우아건설", "🏗️", "건설업 등록 업체", "wooaconstruct.wooahouse.com", "wooaconstruct/_rawdata/con_*.json", False, None),
    ("wooapay", "우아페이", "💳", "지역화폐 가맹점", "wooapay.wooahouse.com", "wooapay/_rawdata/pay_*.json", False, None),
    ("wooahagwon", "우아학원", "📚", "학원·교습소 수강료", "wooahagwon.wooahouse.com", "wooahagwon/_rawdata/leaf_*.json", False, None),
    ("wooagym", "우아헬스장", "💪", "헬스장·피트니스·체력단련장", "wooagym.wooahouse.com", "wooagym/_rawdata/hub_items.json", True, None),
    ("wooavet", "우아동물병원", "🐾", "동물병원", "wooavet.wooahouse.com", "wooavet/_rawdata/hub_items.json", True, None),
    ("wooakinder", "우아유치원", "🏫", "유치원", "wooakinder.wooahouse.com", "wooakinder/_rawdata/hub_items.json", True, "note"),
    ("wooasenior", "우아경로당", "🏘️", "경로당·마을회관", "wooasenior.wooahouse.com", "wooasenior/_rawdata/hub_items.json", True, "note"),
    ("wooagreen", "우아그린", "🌳", "도시공원·근린공원", "wooagreen.wooahouse.com", "wooagreen/_rawdata/hub_items.json", True, "note"),
    ("hosppass", "우아병원", "🏥", "병원·의원·약국", "hosppass.wooahouse.com", None, False, "label"),
]


def load_hosppass():
    """hosppass/docs/지역/{시도}/{시군구}.json 의 병원·약국(읍면동 emd_nm 포함)을 평탄화."""
    base = os.path.join(ROOT, "hosppass", "docs", "지역")
    out = []
    for f in glob.glob(os.path.join(base, "*", "*.json")):
        dirname = os.path.basename(os.path.dirname(f))
        do = "세종" if dirname == "세종시" else dirname
        d = json.load(open(f, encoding="utf-8"))
        for kind, lst in (("h", d.get("hospitals", [])), ("p", d.get("pharmacies", []))):
            for h in lst:
                out.append({"doShort": do, "sigungu_raw": d.get("sggu", ""), "dong": h.get("emd_nm"),
                            "label": (h.get("cl_nm") or "병원") if kind == "h" else "약국",
                            "lat": h.get("y"), "lng": h.get("x"), "dir": dirname})
    return out
SRC_META = {s[0]: dict(name=s[1], icon=s[2], desc=s[3], domain=s[4], district=s[6]) for s in SOURCES}


def load_items(pattern):
    files = [f for f in sorted(glob.glob(os.path.join(ROOT, pattern))) if "raw" not in os.path.basename(f)]
    for f in files:
        for it in json.load(open(f, encoding="utf-8")):
            yield it


def q(s):
    return quote(str(s), safe="")


def main():
    items_by_src = {}
    for key, *_rest in SOURCES:
        pat = [s for s in SOURCES if s[0] == key][0][5]
        items_by_src[key] = load_hosppass() if pat is None else list(load_items(pat))
        print(f"[{key}] {len(items_by_src[key]):,}건", flush=True)

    # ---- 1) hub_data.json: 시도별 개수
    hub_path = os.path.join(DOCS, "hub_data.json")
    hub = json.load(open(hub_path, encoding="utf-8"))
    for key, name, icon, desc, domain, _pat, _d, _sub in SOURCES:
        if _pat is None:   # hosppass 는 기존 hub_data 항목(우아병원) 유지
            continue
        counts = Counter(it["doShort"] for it in items_by_src[key])
        hub[key] = {"name": name, "icon": icon, "desc": desc, "domain": domain,
                    "counts": {r: counts.get(r, 0) for r in CANON}, "total": sum(counts.values())}
    json.dump(hub, open(hub_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- 2) 기준 동 (구 단위 사이트)
    master = {}            # (do, sg, dong) -> sgSlug
    city_idx = defaultdict(set)   # (do, city, dong) -> {sg_full}
    sg_set = set()         # (do, sg_full)
    for key, *_ in SOURCES:
        if not SRC_META[key]["district"]:
            continue
        for it in items_by_src[key]:
            dg = it.get("dong")
            if not dg or dg == "기타":
                continue
            k = (it["doShort"], it["sigungu"], dg)
            master.setdefault(k, it.get("sgSlug") or it["sigungu"].replace(" ", "-"))
            city_idx[(it["doShort"], it["sigungu"].split()[0], dg)].add(it["sigungu"])
            sg_set.add((it["doShort"], it["sigungu"]))
    sg_slug = {}
    for (d, sg, dg), slug in master.items():
        sg_slug[(d, sg)] = slug
    print(f"기준 동 {len(master):,}개, 시군구 {len(sg_slug):,}개")

    # hosppass: '수원팔달구' 같은 축약 시군구명을 기준 시군구('수원시 팔달구')로 매핑하고, 기준에 없던 동은 추가
    def sgn(s):
        return str(s).replace(" ", "").replace("시", "")
    norm_idx = {(d, sgn(sg)): sg for (d, sg) in sg_slug}
    hp_sg_link = {}
    for it in items_by_src["hosppass"]:
        sg = norm_idx.get((it["doShort"], sgn(it["sigungu_raw"])))
        it["sigungu"] = sg or "-"
        if sg:
            hp_sg_link[(it["doShort"], sg)] = f"https://hosppass.wooahouse.com/지역/{q(it['dir'])}/{q(it['sigungu_raw'])}.html"
            it["link"] = hp_sg_link[(it["doShort"], sg)]
            dg = it.get("dong")
            if dg and dg != "기타":
                k = (it["doShort"], sg, dg)
                if k not in master:
                    master[k] = sg_slug[(it["doShort"], sg)]
                    city_idx[(it["doShort"], sg.split()[0], dg)].add(sg)

    def resolve(it):
        """아이템을 기준 동 키로 매핑. 불가하면 None."""
        d, sg, dg = it["doShort"], it.get("sigungu"), it.get("dong")
        if not dg or dg == "기타" or not sg or sg == "-":
            return None
        if (d, sg, dg) in master:
            return (d, sg, dg)
        cands = city_idx.get((d, sg.split()[0], dg), set())
        if len(cands) == 1:
            return (d, next(iter(cands)), dg)
        return None

    dongs = {}
    def slot(k):
        if k not in dongs:
            dongs[k] = {"do": k[0], "sg": k[1], "sgSlug": sg_slug[(k[0], k[1])], "dong": k[2],
                        "counts": {}, "sub": {}, "links": {}}
        return dongs[k]

    sg_counts = defaultdict(lambda: defaultdict(int))
    sg_links = defaultdict(dict)
    stat = {}
    for key, name, icon, desc, domain, _pat, district, subf in SOURCES:
        mapped = unmapped = 0
        cnt = defaultdict(int)
        sub = defaultdict(Counter)
        link_seg = {}
        custom_link = {}
        for it in items_by_src[key]:
            k = resolve(it)
            if k is not None and it.get("link"):
                custom_link[k] = it["link"]
            if k is None:
                unmapped += 1
                # 시군구 단위 집계에는 구 단위 사이트의 '기타' 동도 포함
                if district and it.get("sigungu") and (it["doShort"], it["sigungu"]) in sg_slug:
                    sg_counts[(it["doShort"], it["sigungu"])][key] += 1
                continue
            mapped += 1
            cnt[k] += 1
            sg_counts[(k[0], k[1])][key] += 1
            if subf:
                sub[k][it.get(subf)] += 1
            if k not in link_seg:
                if district:
                    link_seg[k] = (it.get("sgSlug") or it["sigungu"].replace(" ", "-"), it["dong"])
                else:
                    link_seg[k] = (it["sigungu"], it["dong"])
        for k, n in cnt.items():
            s = slot(k)
            s["counts"][key] = n
            seg = link_seg[k]
            s["links"][key] = custom_link.get(k) or f"https://{domain}/region/{q(k[0])}/{q(seg[0])}/{q(seg[1])}/"
            if subf:
                s["sub"][key] = [[lab, c] for lab, c in sub[k].most_common(4)]
        stat[key] = (mapped, unmapped)
        print(f"  {key}: 동 매핑 {mapped:,} / 미매핑 {unmapped:,}")

    # 시군구 링크 (시 단위 사이트는 구 단위 시군구에서 시 페이지로 링크)
    for (d, sg), slug in sg_slug.items():
        city = sg.split()[0]
        for key, name, icon, desc, domain, _pat, district, _sub in SOURCES:
            if key == "hosppass":
                if (d, sg) in hp_sg_link:
                    sg_links[(d, sg)][key] = hp_sg_link[(d, sg)]
            elif district:
                sg_links[(d, sg)][key] = f"https://{domain}/region/{q(d)}/{q(slug)}/"
            else:
                sg_links[(d, sg)][key] = f"https://{domain}/region/{q(d)}/{q(city)}/"

    # ---- 3) 동 중심 좌표 (간식·복권 허브 좌표 + 레저 시설 좌표)
    pts = defaultdict(list)
    for p, keyfn in (("wooasnack/_rawdata/dongs.json", lambda d: (d["do"], d["sigungu"], d["dong"])),
                     ("wooalotto/_rawdata/dongs.json", lambda d: (d["do"], d["sigungu"], d["dong"]))):
        fp = os.path.join(ROOT, p)
        if os.path.exists(fp):
            for d in json.load(open(fp, encoding="utf-8")):
                if d.get("lat") is not None:
                    pts[keyfn(d)].append((d["lat"], d["lng"]))
    for it in items_by_src["wooaleisure"]:
        if it.get("lat") not in ("", None) and it.get("dong") != "기타":
            pts[(it["doShort"], it["sigungu"], it["dong"])].append((float(it["lat"]), float(it["lng"])))
    for it in items_by_src["hosppass"]:
        if it.get("lat") and it.get("lng"):
            kk = resolve(it)
            if kk is not None:
                pts[kk].append((float(it["lat"]), float(it["lng"])))
    cen = {k: (sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v)) for k, v in pts.items() if v}
    keys = [k for k in dongs.keys() if k in cen]
    lat = np.array([cen[k][0] for k in keys]); lng = np.array([cen[k][1] for k in keys])
    p = math.pi / 180
    near = {}
    CH = 500
    for s in range(0, len(keys), CH):
        a = np.sin((lat[None, :] - lat[s:s + CH, None]) * p / 2) ** 2 + \
            np.cos(lat[s:s + CH, None] * p) * np.cos(lat[None, :] * p) * np.sin((lng[None, :] - lng[s:s + CH, None]) * p / 2) ** 2
        d = 12742 * np.arcsin(np.sqrt(a))
        for r in range(d.shape[0]):
            d[r, s + r] = 1e9
        idx = np.argsort(d, axis=1)[:, :8]
        for r in range(idx.shape[0]):
            near[keys[s + r]] = [(keys[j], round(float(d[r, j]), 1)) for j in idx[r] if d[r, j] <= 6.0]
    for k, lst in near.items():
        dongs[k]["near"] = [[kk[0], kk[1], kk[2], km] for kk, km in lst]
        dongs[k]["lat"], dongs[k]["lng"] = round(cen[k][0], 5), round(cen[k][1], 5)

    # ---- 4) 직렬화
    out_dongs = {}
    for v in dongs.values():
        v["total"] = sum(v["counts"].values())
    for k, v in dongs.items():
        v["near"] = v.get("near", [])
        # 근처 동의 slug/합계 정보 보강
        v["near"] = [[kk0, kk1, sg_slug.get((kk0, kk1), kk1.replace(" ", "-")), kk2, km, dongs.get((kk0, kk1, kk2), {}).get("total", 0)] for kk0, kk1, kk2, km in v["near"]]
        out_dongs["|".join(k)] = v
    out_sg = {}
    sg_dongs = defaultdict(list)
    for k, v in dongs.items():
        sg_dongs[(k[0], k[1])].append([k[2], v["total"]])
    for (d, sg), slug in sg_slug.items():
        counts = dict(sg_counts.get((d, sg), {}))
        out_sg["|".join((d, sg))] = {"do": d, "sg": sg, "sgSlug": slug, "counts": counts, "total": sum(counts.values()),
                                       "links": sg_links[(d, sg)], "dongs": sorted(sg_dongs.get((d, sg), []), key=lambda x: (-x[1], x[0]))}
    json.dump({"sources": SRC_META, "dongs": out_dongs, "sigungu": out_sg}, open(os.path.join(CACHE, "dong_hub.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"동 허브 {len(out_dongs):,}개, 시군구 허브 {len(out_sg):,}개 저장")


if __name__ == "__main__":
    main()
