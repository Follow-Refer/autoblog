"""amazon_refresh.js 결과(도구 결과 저장 파일들)로 products.json 재생성.
사용: python tools/build_products.py <결과파일1> <결과파일2> ...
- 죽은 상품 제거, 새 베스트셀러 추가, 기존 상품은 최신 가격·평점으로 갱신
- 기준: 평점 4.3+, 평가 2,000개+, 특징 3개+, 가격 있음, 흥미 없는 소모품 제외"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "products.json")
DROP = re.compile(r"paper towel|trash bag|cotton (swab|round|ball)|q-tips|straws|parchment|liners|hair ties|razor|blades|"
                  r"hoodie|sweatshirt|sweatpant|jogger|leggings|pants|pee pads|poop bags|diapers|training pants|cat food|dog food|"
                  r"litter|wrap,|nipple|mustache|hair dye|hair color|gray hair|lash adhesive|refill|replacement|tablets for|"
                  r"toilet bowl|timer|can opener|shears|scissors|hangers|hooks|shoe rack|sponge holder|kitchen scale|"
                  r"sealer bags|burner|moving bags|lunch b|ice cube|drying mat|drops for infants|storage bags|storage cubes|disinfecting|cleaner spray", re.I)
NAMES = {"skincare": "skincare", "haircare": "hair care", "beauty-tools": "beauty tools", "kitchen": "kitchen appliances",
         "kitchen-tools": "kitchen gadgets", "storage": "home organization", "fitness": "fitness gear",
         "pet": "pet supplies", "baby": "baby essentials", "health": "personal care"}


def load_results(path):
    dec = json.JSONDecoder()
    txt = open(path, encoding="utf-8").read()
    obj, _ = dec.raw_decode(txt.strip())
    while isinstance(obj, list) and obj and isinstance(obj[0], dict) and "text" in obj[0]:
        obj = obj[0]["text"]
    while isinstance(obj, str):
        obj, _ = dec.raw_decode(obj.strip())
    return obj


def fix_price(p):
    p = (p or "").strip()
    if re.fullmatch(r"\$\d{3,5}", p):
        p = "$" + p[1:-2] + "." + p[-2:]
    return p


def ok(p):
    try:
        cnt = int(re.sub(r"\D", "", p.get("review_count", "")) or 0)
        rating = float((p.get("rating") or "0").split()[0])
    except ValueError:
        return False
    return (p.get("title") and p.get("price") and len(p.get("features", [])) >= 3
            and rating >= 4.3 and cnt >= 2000 and not DROP.search(p["title"]))


def main(files):
    old = json.load(open(PATH, encoding="utf-8"))
    old_by = {p["asin"]: p for p in old["products"]}
    results = []
    for f in files:
        results += load_results(f)
    if len(results) < 50:
        sys.exit(f"결과가 너무 적음({len(results)}개) — 수집 실패로 보고 기존 목록 유지")
    today = datetime.date.today().isoformat()
    seen, out, dead, added = set(), [], [], []
    for r in results:
        a = r.get("asin")
        if not a or a in seen:
            continue
        seen.add(a)
        if r.get("dead"):
            if a in old_by:
                dead.append(old_by[a]["title"][:60])
            continue
        if r.get("error") or not r.get("title"):
            if a in old_by:            # 일시 오류면 기존 정보 유지
                out.append(old_by[a])
            continue
        r["price"] = fix_price(r["price"])
        if a in old_by:
            r["category"] = old_by[a]["category"]
            r["added_on"] = old_by[a].get("added_on", old_by[a].get("verified_on", today))
        elif not ok(r):
            continue
        else:
            r["added_on"] = today
            added.append(r["title"][:60])
        r["verified"] = True
        r["verified_on"] = today
        out.append(r)
    json.dump({"updated": today, "category_names": NAMES, "products": out},
              open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"총 {len(out)}개 | 추가 {len(added)} | 제거(단종) {len(dead)}")
    for t in added:
        print("  + " + t)
    for t in dead:
        print("  - " + t)


if __name__ == "__main__":
    main(sys.argv[1:])
