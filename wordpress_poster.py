import requests
import os
import base64

WP_URL      = os.environ["WP_URL"]          # https://follow-refer.com
WP_USER     = os.environ["WP_USERNAME"]     # choihansam
WP_PASSWORD = os.environ["WP_APP_PASSWORD"] # Application Password

def get_auth_header():
    token = base64.b64encode(f"{WP_USER}:{WP_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def get_or_create_category(name: str) -> int:
    """카테고리 찾기 또는 생성"""
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    
    # 기존 카테고리 검색
    resp = requests.get(f"{WP_URL}/wp-json/wp/v2/categories?search={name}", headers=headers)
    cats = resp.json()
    if cats:
        return cats[0]["id"]
    
    # 새 카테고리 생성
    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/categories",
        json={"name": name},
        headers=headers
    )
    return resp.json().get("id", 1)

def get_or_create_tags(tag_names: list) -> list:
    """태그 찾기 또는 생성"""
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    tag_ids = []
    
    for name in tag_names[:5]:  # 최대 5개
        resp = requests.get(f"{WP_URL}/wp-json/wp/v2/tags?search={name}", headers=headers)
        tags = resp.json()
        if tags:
            tag_ids.append(tags[0]["id"])
        else:
            resp = requests.post(
                f"{WP_URL}/wp-json/wp/v2/tags",
                json={"name": name},
                headers=headers
            )
            if resp.status_code == 201:
                tag_ids.append(resp.json().get("id"))
    
    return tag_ids

def post_to_wordpress(post_data: dict, lang: str = "ko"):
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    
    product = post_data.get("product", {})
    category_name = f"{'리뷰' if lang == 'ko' else 'Review'} - {product.get('category', 'general').title()}"
    
    category_id = get_or_create_category(category_name)
    tag_ids = get_or_create_tags(post_data.get("tags", []))

    # 언어별 커스텀 필드 (다국어 플러그인 없이 slug로 구분)
    slug_suffix = "-kr" if lang == "ko" else "-en"
    
    payload = {
        "title":      post_data["title"],
        "content":    post_data["content"],
        "excerpt":    post_data.get("excerpt", ""),
        "status":     "publish",
        "categories": [category_id],
        "tags":       tag_ids,
        "slug":       generate_slug(post_data["title"]) + slug_suffix,
        "meta": {
            "lang": lang
        }
    }

    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json=payload,
        headers=headers,
        timeout=30, verify=False
    )

    if resp.status_code == 201:
        post = resp.json()
        print(f"  발행 성공: {post['link']}")
        return post
    else:
        print(f"  발행 실패: {resp.status_code} - {resp.text[:200]}")
        return None

def generate_slug(title: str) -> str:
    import re
    # 영문/숫자만 남기고 슬러그 생성
    slug = re.sub(r'[^a-zA-Z0-9가-힣\s]', '', title)
    slug = slug.lower().replace(' ', '-')[:60]
    return slug or "product-review"
