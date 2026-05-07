import requests
import os
import base64
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WP_URL      = os.environ["WP_URL"]
WP_USER     = os.environ["WP_USERNAME"]
WP_PASSWORD = os.environ["WP_APP_PASSWORD"]

def get_auth_header():
    token = base64.b64encode((WP_USER + ":" + WP_PASSWORD).encode()).decode()
    return {"Authorization": "Basic " + token}

def get_or_create_category(name: str) -> int:
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    for attempt in range(3):
        try:
            resp = requests.get(WP_URL + "/wp-json/wp/v2/categories?search=" + name, headers=headers, timeout=60, verify=True)
            cats = resp.json()
            if cats and isinstance(cats, list):
                return cats[0]["id"]
            resp = requests.post(WP_URL + "/wp-json/wp/v2/categories", json={"name": name}, headers=headers, timeout=60, verify=True)
            return resp.json().get("id", 1)
        except Exception as e:
            print(f"  Category retry {attempt+1}/3: {e}")
            time.sleep(10)
    return 1

def get_or_create_tags(tag_names: list) -> list:
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    tag_ids = []
    for name in tag_names[:5]:
        for attempt in range(3):
            try:
                resp = requests.get(WP_URL + "/wp-json/wp/v2/tags?search=" + name, headers=headers, timeout=60, verify=True)
                tags = resp.json()
                if tags and isinstance(tags, list):
                    tag_ids.append(tags[0]["id"])
                else:
                    resp = requests.post(WP_URL + "/wp-json/wp/v2/tags", json={"name": name}, headers=headers, timeout=60, verify=True)
                    if resp.status_code == 201:
                        tag_ids.append(resp.json().get("id"))
                break
            except Exception as e:
                print(f"  Tag retry {attempt+1}/3: {e}")
                time.sleep(10)
    return tag_ids

def post_to_wordpress(post_data: dict, lang: str = "en"):
    headers = {**get_auth_header(), "Content-Type": "application/json"}
    product = post_data.get("product", {})
    category_name = "Review - " + product.get("category", "general").title()
    category_id = get_or_create_category(category_name)
    tag_ids = get_or_create_tags(post_data.get("tags", []))

    import re
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
                timeout=60,
                verify=True
            )
            if resp.status_code == 201:
                post = resp.json()
                print("  Published: " + post.get("link", "ok"))
                return post
            else:
                print("  Failed: " + str(resp.status_code))
                return None
        except Exception as e:
            print(f"  Post retry {attempt+1}/3: {e}")
            time.sleep(10)
    return None
