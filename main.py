import json
import os
import random
import time

from content_generator import generate_guide, generate_post
from link_checker import DEAD, check_asin
from wordpress_poster import is_duplicate_asin, post_to_wordpress

# products.json — 아마존 베스트셀러에서 실제 상품 페이지를 하나씩 확인해 만든 목록
# (상품번호·제목·가격·평점·특징이 모두 실제 페이지 기준)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "products.json"), encoding="utf-8") as f:
    DATA = json.load(f)
PRODUCTS = DATA["products"]
CATEGORY_NAMES = DATA["category_names"]


def pick_single():
    """이미 올린 상품·죽은 링크는 건너뛰고 하나 고르기."""
    pool = PRODUCTS[:]
    random.shuffle(pool)
    for p in pool[:15]:
        if is_duplicate_asin(p["asin"]):
            continue
        p["_link_status"] = check_asin(p["asin"])
        print(f"  {p['title'][:50]} → {p['_link_status']}")
        if p["_link_status"] != DEAD:
            return p
    return None


def pick_guide():
    """같은 카테고리 상위 상품 3개로 비교 추천글."""
    by_cat = {}
    for p in PRODUCTS:
        by_cat.setdefault(p["category"], []).append(p)
    cat = random.choice([c for c, ps in by_cat.items() if len(ps) >= 3])
    pool = by_cat[cat][:]
    random.shuffle(pool)
    chosen = []
    for p in pool:
        p["_link_status"] = check_asin(p["asin"])
        if p["_link_status"] != DEAD:
            chosen.append(p)
        if len(chosen) == 3:
            break
    return cat, chosen


def main():
    lang = os.environ.get("BLOG_LANG", "en")
    print(f"=== AutoBlog Start (lang={lang}) ===")

    wait = random.randint(0, 1200)
    print(f"Waiting {wait//60} minutes...")
    time.sleep(wait)

    post = None
    if random.random() < 0.3:
        cat, products = pick_guide()
        if len(products) >= 3:
            print(f"Today: guide — {CATEGORY_NAMES.get(cat, cat)}")
            post = generate_guide(products, CATEGORY_NAMES.get(cat, cat), lang=lang)

    if post is None:
        product = pick_single()
        if not product:
            print("No usable product found.")
            return
        product["category_label"] = CATEGORY_NAMES.get(product["category"], product["category"])
        print(f"Today: review — {product['title'][:60]}")
        post = generate_post(product, lang=lang)

    result = post_to_wordpress(post, lang=lang)
    if result:
        print(f"::notice::Published ({lang}): {result.get('link', 'ok')}")
    print(f"=== AutoBlog Done (lang={lang}) ===")


if __name__ == "__main__":
    main()
