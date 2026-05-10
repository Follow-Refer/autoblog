import requests
from bs4 import BeautifulSoup
import random
import time
import re

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    },
]

def get_amazon_reviews(product_url: str) -> dict:
    """아마존 실제 구매자 리뷰 수집 — 구체적인 경험담 위주로"""
    try:
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
        if not asin_match:
            return {"pros": [], "cons": []}

        asin = asin_match.group(1)
        review_url = f"https://www.amazon.com/product-reviews/{asin}/?sortBy=helpful&reviewerType=avp_only_reviews"

        time.sleep(random.uniform(2, 4))
        headers = random.choice(HEADERS_LIST)
        resp = requests.get(review_url, headers=headers, timeout=15)

        if resp.status_code != 200:
            return {"pros": [], "cons": []}

        soup = BeautifulSoup(resp.text, "html.parser")
        review_elements = soup.select("div[data-hook='review']")

        if not review_elements:
            return {"pros": [], "cons": []}

        pros = []
        cons = []

        for review in review_elements[:30]:
            rating_el = review.select_one("i[data-hook='review-star-rating'] span, i[data-hook='cmps-review-star-rating'] span")
            if not rating_el:
                continue

            rating_text = rating_el.get_text(strip=True)
            try:
                rating = float(rating_text.split(" ")[0])
            except:
                continue

            # 리뷰 제목 + 본문 합쳐서 활용
            title_el = review.select_one("a[data-hook='review-title'] span:not(.a-icon-alt), span[data-hook='review-title']")
            body_el = review.select_one("span[data-hook='review-body'] span")

            title_text = title_el.get_text(strip=True) if title_el else ""
            body_text = body_el.get_text(strip=True) if body_el else ""

            # 제목과 본문에서 구체적인 내용 추출
            combined = (title_text + " — " + body_text).strip() if title_text else body_text

            # 너무 짧거나 의미없는 리뷰 스킵
            if len(combined) < 30:
                continue

            # 200자로 제한
            combined = combined[:200]

            if rating >= 4.0 and len(pros) < 5:
                pros.append(combined)
            elif rating <= 2.0 and len(cons) < 3:
                cons.append(combined)

        return {
            "pros": pros[:4],
            "cons": cons[:2],
        }

    except Exception as e:
        print(f"  리뷰 스크래핑 실패: {e}")
        return {"pros": [], "cons": []}
