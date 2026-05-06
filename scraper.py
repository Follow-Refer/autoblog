import requests
from bs4 import BeautifulSoup
import random
import time

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
]

CATEGORY_URLS = {
    "kitchen":      "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/",
    "electronics":  "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/",
    "beauty":       "https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/",
    "fitness":      "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/",
    "home":         "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/",
    "outdoor":      "https://www.amazon.com/Best-Sellers-Patio-Lawn-Garden/zgbs/lawn-garden/",
    "baby":         "https://www.amazon.com/Best-Sellers-Baby-Products/zgbs/baby-products/",
    "pet-supplies": "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/",
}

def get_bestseller_products(category: str, count: int = 3) -> list:
    url = CATEGORY_URLS.get(category, CATEGORY_URLS["kitchen"])
    headers = random.choice(HEADERS_LIST)
    
    try:
        time.sleep(random.uniform(2, 4))
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        products = []
        items = soup.select("div.zg-grid-general-faceout")[:count * 3]

        for item in items:
            if len(products) >= count:
                break

            title_el = item.select_one("div._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y, .p13n-sc-truncated, span.a-size-base")
            price_el = item.select_one("span.p13n-sc-price, .a-price .a-offscreen")
            rating_el = item.select_one("span.a-icon-alt")
            link_el = item.select_one("a.a-link-normal")
            img_el = item.select_one("img.a-dynamic-image, img.p13n-product-image")

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            price = price_el.get_text(strip=True) if price_el else "Price not available"
            rating = rating_el.get_text(strip=True) if rating_el else "4.5 out of 5 stars"
            link = "https://www.amazon.com" + link_el["href"] if link_el and link_el.get("href") else url
            image = img_el.get("src", "") if img_el else ""

            # 아마존 어필리에이트 태그 추가 (나중에 실제 태그로 교체)
            if "?" in link:
                link += "&tag=followrefer-20"
            else:
                link += "?tag=followrefer-20"

            products.append({
                "title": title,
                "price": price,
                "rating": rating,
                "link": link,
                "image": image,
                "category": category,
            })

        # 스크래핑 실패시 fallback 데이터
        if not products:
            products = get_fallback_products(category, count)

        return products[:count]

    except Exception as e:
        print(f"스크래핑 오류: {e}")
        return get_fallback_products(category, count)


def get_fallback_products(category: str, count: int) -> list:
    """스크래핑 실패시 사용할 샘플 데이터"""
    fallbacks = {
        "kitchen": [
            {"title": "Instant Pot Duo 7-in-1 Electric Pressure Cooker", "price": "$89.99", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B00FLYWNYQ?tag=followrefer-20", "image": "", "category": "kitchen"},
            {"title": "Lodge Cast Iron Skillet 12 Inch", "price": "$34.90", "rating": "4.8 out of 5 stars", "link": "https://www.amazon.com/dp/B00G2XGC88?tag=followrefer-20", "image": "", "category": "kitchen"},
            {"title": "OXO Good Grips 3-Piece Mixing Bowl Set", "price": "$28.99", "rating": "4.6 out of 5 stars", "link": "https://www.amazon.com/dp/B0000CFLJA?tag=followrefer-20", "image": "", "category": "kitchen"},
        ],
        "electronics": [
            {"title": "Apple AirPods Pro (2nd Generation)", "price": "$189.00", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B0BDHWDR12?tag=followrefer-20", "image": "", "category": "electronics"},
            {"title": "Anker 313 USB-C to USB-C Cable", "price": "$10.99", "rating": "4.6 out of 5 stars", "link": "https://www.amazon.com/dp/B09F52XQSV?tag=followrefer-20", "image": "", "category": "electronics"},
            {"title": "Amazon Echo Dot (5th Gen)", "price": "$49.99", "rating": "4.5 out of 5 stars", "link": "https://www.amazon.com/dp/B09B8V1LZ3?tag=followrefer-20", "image": "", "category": "electronics"},
        ],
    }
    data = fallbacks.get(category, fallbacks["kitchen"])
    return data[:count]
