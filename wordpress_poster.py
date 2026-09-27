import requests
import os
import base64
import time
import re

WP_URL      = os.environ["WP_URL"]
WP_USER     = os.environ["WP_USERNAME"]
WP_PASSWORD = os.environ["WP_APP_PASSWORD"]

def get_auth_header():
    token = base64.b64encode((WP_USER + ":" + WP_PASSWORD).encode()).decode()
    return {"Authorization": "Basic " + token}

def get_published_asins() -> list:
    """이미 발행된 글의 ASIN 목록 가져오기"""
    headers = get_auth_header()
    asins = []
    try:
        page = 1
        while True:
            resp = requests.get(
                WP_URL + "/wp-json/wp/v2/posts?per_page=100&page=" + str(page),
                headers=headers,
                timeout=30
            )
            posts = resp.json()
            if not posts or not isinstance(posts, list) or len(posts) == 0:
                break
            for post in posts:
                # 슬러그에서 ASIN 힌트 추출 또는 태그에서 찾기
                tags = post.get("tags", [])
                slug = post.get("slug", "")
                asins.append(slug)
            if len(posts) < 100:
                break
            page += 1
    except Exception as e:
        print(f"  ASIN 목록 가져오기 오류: {e}")
    return asins

def get_published_slugs() -> list:
    """이미 발행된 글의 슬러그 목록 가져오기"""
    headers = get_auth_header()
    slugs = []
    try:
        page = 1
        while True:
            resp = requests.get(
                WP_URL + "/wp-json/wp/v2/posts?per_page=100&page=" + str(page),
                headers=headers,
                timeout=30
            )
            posts = resp.json()
            if not posts or not isinstance(posts, list) or len(posts) == 0:
                break
            for post in posts:
                slugs.append(post.get("slug", ""))
            if len(posts) < 100:
                break
            page += 1
    except Exception as e:
        print(f"  슬러그 목록 오류: {e}")
    return slugs

def get_published_asins_from_tags() -> list:
    """태그에서 ASIN 목록 가져오기"""
    headers = get_auth_header()
    asins = []
    try:
        resp = requests.get(
            WP_URL + "/wp-json/wp/v2/tags?per_page=100&search=asin",
            headers=headers,
            timeout=30
        )
        tags = resp.json()
        if tags and isinstance(tags, list):
            for tag in tags:
                name = tag.get("name", "")
                if name.startswith("asin-"):
                    asins.append(name.replace("asin-", ""))
    except Exception as e:
        print(f"  ASIN 태그 오류: {e}")
    return asins

def is_duplicate_asin(asin: str) -> bool:
    """ASIN 기반 중복 체크"""
    if not asin:
        return False
    try:
        headers = get_auth_header()
        resp = requests.get(
            WP_URL + "/wp-json/wp/v2/tags?search=asin-" + asin,
            headers=headers,
            timeout=30
        )
        tags = resp.json()
        if tags and isinstance(tags, list) and len(tags) > 0:
            for tag in tags:
                if tag.get("name") == "asin-" + asin:
                    print(f"  Duplicate ASIN {asin}, skipping...")
                    return True
    except Exception as e:
        print(f"  ASIN 중복 체크 오류: {e}")
    return False

def get_or_create_category(name: str) -> int:
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    try:
        resp = requests.get(WP_URL + "/wp-json/wp/v2/categories?search=" + name, headers=headers, timeout=60)
        cats = resp.json()
        if cats and isinstance(cats, list) and len(cats) > 0:
            return cats[0]["id"]
        resp = requests.post(WP_URL + "/wp-json/wp/v2/categories", json={"name": name}, headers=headers, timeout=60)
        return resp.json().get("id", 1)
    except Exception as e:
        print(f"  Category error: {e}")
        return 1

def get_or_create_tags(tag_names: list) -> list:
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    tag_ids = []
    for name in tag_names[:5]:
        try:
            resp = requests.get(WP_URL + "/wp-json/wp/v2/tags?search=" + name, headers=headers, timeout=60)
            tags = resp.json()
            if tags and isinstance(tags, list) and len(tags) > 0:
                tag_ids.append(tags[0]["id"])
            else:
                resp = requests.post(WP_URL + "/wp-json/wp/v2/tags", json={"name": name}, headers=headers, timeout=60)
                if resp.status_code == 201:
                    tag_ids.append(resp.json().get("id"))
        except Exception as e:
            print(f"  Tag error: {e}")
    return tag_ids

def post_to_wordpress(post_data: dict, lang: str = "en"):
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    product = post_data.get("product", {})
    asin = product.get("asin", "")

    # ASIN 기반 중복 체크
    if asin and is_duplicate_asin(asin):
        return None

    category_name = "Review - " + product.get("category_label", product.get("category", "general")).title()
    category_id = get_or_create_category(category_name)

    # 태그에 ASIN 추가 (중복 체크용)
    tags = post_data.get("tags", [])
    if asin:
        tags.append("asin-" + asin)
    tag_ids = get_or_create_tags(tags)

    slug = re.sub(r'[^a-zA-Z0-9\s]', '', post_data["title"])
    slug = slug.lower().replace(' ', '-')[:60]

    payload = {
        "title":      post_data["title"],
        "content":    post_data["content"],
        "excerpt":    post_data.get("excerpt", ""),
        "status":     "publish",
        "categories": [category_id],
        "tags":       tag_ids,
        "slug":       slug or "product-review",
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                WP_URL + "/wp-json/wp/v2/posts",
                json=payload,
                headers=headers,
                timeout=60
            )
            if resp.status_code == 201:
                post = resp.json()
                print("  Published: " + post.get("link", "ok"))
                return post
            elif resp.status_code == 400:
                print("  Duplicate slug, skipping...")
                return None
            else:
                print("  Failed: " + str(resp.status_code))
                return None
        except Exception as e:
            print(f"  Retry {attempt+1}/3: {e}")
            time.sleep(10)
    return None
