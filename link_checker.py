"""아마존 링크 검사 — 단종/삭제 상품이면 '개 사진' 페이지 대신 검색 링크로 대체."""
import random
import re
import time
import urllib.parse

import requests

AMAZON_ID = "followrefer20-20"

HEADERS = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    },
]

DEAD, ALIVE, UNKNOWN = "dead", "alive", "unknown"


def extract_asin(url: str) -> str:
    m = re.search(r"/dp/([A-Z0-9]{10})", url or "")
    return m.group(1) if m else ""


def check_asin(asin: str) -> str:
    """dead = 확실히 없는 상품(404 / 'couldn't find that page'),
    alive = 상품 페이지 확인됨, unknown = 아마존이 봇 차단해서 판단 불가."""
    if not asin:
        return UNKNOWN
    try:
        time.sleep(random.uniform(1.0, 2.5))
        r = requests.get(
            f"https://www.amazon.com/dp/{asin}",
            headers=random.choice(HEADERS),
            timeout=15,
            allow_redirects=True,
        )
        text = r.text or ""
        if r.status_code == 404 or "couldn't find that page" in text or "Page Not Found" in text:
            return DEAD
        if r.status_code == 200 and 'id="productTitle"' in text:
            return ALIVE
        return UNKNOWN
    except Exception as e:
        print(f"  링크 검사 오류 ({asin}): {e}")
        return UNKNOWN


def search_link(title: str) -> str:
    """상품명으로 아마존 검색 링크 — 절대 죽지 않고, 24시간 안 구매 전부 수수료 대상."""
    short = re.sub(r"[,|(].*$", "", title or "").strip()[:80] or (title or "")[:80]
    q = urllib.parse.quote_plus(short)
    return f"https://www.amazon.com/s?k={q}&tag={AMAZON_ID}"


def dp_link(asin: str) -> str:
    return f"https://www.amazon.com/dp/{asin}?tag={AMAZON_ID}"


def best_link(product: dict) -> str:
    """살아있는 게 확인되면 상품 페이지, 아니면 검색 링크."""
    asin = product.get("asin") or extract_asin(product.get("link", ""))
    status = product.get("_link_status") or check_asin(asin)
    product["_link_status"] = status
    if status == ALIVE and asin:
        return dp_link(asin)
    return search_link(product.get("title", ""))
