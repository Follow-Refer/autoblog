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
    """
    아마존 상품 링크에서 실제 리뷰를 가져옵니다.
    별점 4~5점 → 장점, 별점 1~2점 → 단점으로 분류합니다.
    """
    try:
        # ASIN 추출
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
        if not asin_match:
            return get_fallback_reviews()
        
        asin = asin_match.group(1)
        review_url = f"https://www.amazon.com/product-reviews/{asin}/?sortBy=recent&reviewerType=all_reviews"

        time.sleep(random.uniform(2, 4))
        headers = random.choice(HEADERS_LIST)
        resp = requests.get(review_url, headers=headers, timeout=15)
        
        if resp.status_code != 200:
            return get_fallback_reviews()

        soup = BeautifulSoup(resp.text, "html.parser")
        review_elements = soup.select("div[data-hook='review']")

        pros = []
        cons = []

        for review in review_elements[:20]:  # 최대 20개 분석
            # 별점 추출
            rating_el = review.select_one("i[data-hook='review-star-rating'] span")
            if not rating_el:
                continue
            rating_text = rating_el.get_text(strip=True)
            rating = float(rating_text.split(" ")[0]) if rating_text else 3.0

            # 리뷰 본문 추출
            body_el = review.select_one("span[data-hook='review-body'] span")
            if not body_el:
                continue
            body = body_el.get_text(strip=True)

            # 너무 짧거나 긴 리뷰 스킵
            if len(body) < 20 or len(body) > 300:
                continue

            if rating >= 4.0 and len(pros) < 5:
                pros.append(body[:150])
            elif rating <= 2.0 and len(cons) < 3:
                cons.append(body[:150])

        # 리뷰가 충분히 없으면 fallback
        if len(pros) < 2:
            return get_fallback_reviews()

        return {
            "pros": pros[:3],  # 장점 최대 3개
            "cons": cons[:2],  # 단점 최대 2개
        }

    except Exception as e:
        print(f"  리뷰 스크래핑 실패: {e}")
        return get_fallback_reviews()


def get_fallback_reviews() -> dict:
    """스크래핑 실패시 기본 리뷰 구조 반환"""
    return {
        "pros": [],
        "cons": [],
    }
