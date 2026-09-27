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
    cache, fixed_posts, fixed_links, checked, errors = {}, 0, 0, 0, 0
    try:
        posts = list(all_posts())
    except Exception as e:
        print(f"::error::글 목록 불러오기 실패: {e}")
        raise
    for post in posts:
      try:
        content = (post.get("content") or {}).get("raw") or ""
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
            print(f"{'OK ' if ok else 'ERR ' + str(r.status_code)} #{post['id']} {post['title']['raw'][:60]}")
      except Exception as e:
        errors += 1
        print(f"::warning::post {post.get('id')}: {e}")
    print(f"::notice::{WP_URL} — 글 {len(posts)}개, 상품 {checked}개 검사, 링크 {fixed_links}개 교체({fixed_posts}개 글), 오류 {errors}")


if __name__ == "__main__":
    main()
