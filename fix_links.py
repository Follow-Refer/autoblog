"""이미 올라간 글의 아마존 링크 일괄 점검.
상품 페이지가 확인되지 않는 링크(단종·삭제)는 상품명 검색 링크로 교체한다.
GitHub Actions의 'Fix Amazon Links' 워크플로에서 수동 실행."""
import base64
import html
import os
import re

import requests

from link_checker import ALIVE, check_asin, search_link

WP_URL = os.environ["WP_URL"].rstrip("/")
AUTH = {"Authorization": "Basic " + base64.b64encode(
    (os.environ["WP_USERNAME"] + ":" + os.environ["WP_APP_PASSWORD"]).encode()).decode()}

LINK_RE = re.compile(r'https://www\.amazon\.com/dp/([A-Z0-9]{10})[^"\'\s<]*')


def product_name(title: str) -> str:
    t = html.unescape(re.sub(r"<[^>]+>", "", title))
    t = re.split(r"[:–—|]| - | Review| Reseña| review", t)[0]
    return t.strip() or title


def all_posts():
    page = 1
    while True:
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts",
                         params={"per_page": 100, "page": page, "context": "edit"},
                         headers=AUTH, timeout=60)
        if r.status_code != 200:
            break
        posts = r.json()
        if not posts:
            break
        yield from posts
        if len(posts) < 100:
            break
        page += 1


def main():
    cache, fixed_posts, fixed_links, checked = {}, 0, 0, 0
    for post in all_posts():
        content = post["content"]["raw"]
        asins = set(LINK_RE.findall(content))
        if not asins:
            continue
        name = product_name(post["title"]["raw"])
        new = content
        for asin in asins:
            if asin not in cache:
                cache[asin] = check_asin(asin)
                checked += 1
            if cache[asin] != ALIVE:
                new = re.sub(r'https://www\.amazon\.com/dp/' + asin + r'[^"\'\s<]*', search_link(name), new)
                fixed_links += 1
                print(f"  [{cache[asin]}] {asin} → search '{name[:50]}'")
        if new != content:
            r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{post['id']}",
                              json={"content": new}, headers=AUTH, timeout=60)
            ok = r.status_code == 200
            fixed_posts += ok
            print(f"{'OK ' if ok else 'ERR'} #{post['id']} {post['title']['raw'][:60]}")
    print(f"\nChecked {checked} products, replaced {fixed_links} links in {fixed_posts} posts.")


if __name__ == "__main__":
    main()
