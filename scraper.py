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
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
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
    "baby":         "https://www.amazon.com/Best-Sellers-Baby-Products/zgbs/baby-products/",
    "pet-supplies": "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/",
}

def extract_asin(url: str) -> str:
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else ""

def get_product_details(url: str) -> dict:
    """상품 상세 페이지에서 실제 스펙/특징 가져오기"""
    try:
        headers = random.choice(HEADERS_LIST)
        time.sleep(random.uniform(2, 4))
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return {}

        soup = BeautifulSoup(resp.text, "html.parser")

        # 정확한 제품명
        title_el = soup.select_one("#productTitle")
        title = title_el.get_text(strip=True) if title_el else ""

        # 가격
        price_el = soup.select_one(".a-price .a-offscreen")
        price = price_el.get_text(strip=True) if price_el else ""

        # 별점
        rating_el = soup.select_one("#acrPopover span.a-icon-alt")
        rating = rating_el.get_text(strip=True) if rating_el else ""

        # 리뷰 수
        review_count_el = soup.select_one("#acrCustomerReviewText")
        review_count = review_count_el.get_text(strip=True) if review_count_el else ""

        # 핵심 특징 (불릿 포인트) - 가장 중요!
        feature_els = soup.select("#feature-bullets li span.a-list-item")
        features = []
        for f in feature_els:
            text = f.get_text(strip=True)
            if len(text) > 15 and "javascript" not in text.lower():
                features.append(text)
        features = features[:8]

        # 기술 스펙 테이블
        specs = {}
        spec_rows = soup.select("#productDetails_techSpec_section_1 tr, #technicalSpecifications_section_1 tr")
        for row in spec_rows[:10]:
            key_el = row.select_one("th")
            val_el = row.select_one("td")
            if key_el and val_el:
                key = key_el.get_text(strip=True)
                val = val_el.get_text(strip=True)
                if key and val:
                    specs[key] = val

        # 상품 이미지
        img_el = soup.select_one("#landingImage, #imgBlkFront")
        image = ""
        if img_el:
            image = img_el.get("src", "") or img_el.get("data-old-hires", "")

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "features": features,
            "specs": specs,
            "image": image,
        }

    except Exception as e:
        print(f"  상품 상세 스크래핑 실패: {e}")
        return {}


def get_bestseller_products(category: str, count: int = 1, exclude_asins: list = []) -> list:
    url = CATEGORY_URLS.get(category, CATEGORY_URLS["kitchen"])
    headers = random.choice(HEADERS_LIST)

    try:
        time.sleep(random.uniform(2, 4))
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        products = []
        items = soup.select("div.zg-grid-general-faceout")
        random.shuffle(items)

        for item in items:
            if len(products) >= count:
                break

            title_el = item.select_one("div._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y, .p13n-sc-truncated, span.a-size-base")
            price_el = item.select_one("span.p13n-sc-price, .a-price .a-offscreen")
            rating_el = item.select_one("span.a-icon-alt")
            link_el = item.select_one("a.a-link-normal")
            img_el = item.select_one("img.a-dynamic-image, img.p13n-product-image")

            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            if len(title) < 5:
                continue

            link = "https://www.amazon.com" + link_el["href"] if link_el.get("href") else url
            asin = extract_asin(link)

            if asin and asin in exclude_asins:
                continue

            price = price_el.get_text(strip=True) if price_el else "Check on Amazon"
            rating = rating_el.get_text(strip=True) if rating_el else "4.5 out of 5 stars"
            image = img_el.get("src", "") if img_el else ""

            # 상품 상세 페이지에서 실제 스펙 가져오기
            print(f"  상품 상세 정보 가져오는 중: {title[:40]}...")
            details = get_product_details(link)

            if details.get("title"):
                title = details["title"]
            if details.get("price"):
                price = details["price"]
            if details.get("rating"):
                rating = details["rating"]
            if details.get("image"):
                image = details["image"]

            sep = "&" if "?" in link else "?"
            affiliate_link = link + sep + "tag=followrefer20-20"

            products.append({
                "title": title,
                "price": price,
                "rating": rating,
                "link": affiliate_link,
                "image": image,
                "category": category,
                "asin": asin,
                "features": details.get("features", []),
                "specs": details.get("specs", {}),
                "review_count": details.get("review_count", ""),
            })

        if not products:
            print("  베스트셀러 스크래핑 실패 → fallback 사용")
            return get_fallback_products(category, count)

        return products[:count]

    except Exception as e:
        print(f"스크래핑 오류: {e}")
        return get_fallback_products(category, count)


def get_fallback_products(category: str, count: int) -> list:
    fallbacks = {
        "kitchen": [
            {
                "title": "Instant Pot Duo 7-in-1 Electric Pressure Cooker, 6 Quart",
                "price": "$89.99", "rating": "4.7 out of 5 stars",
                "link": "https://www.amazon.com/dp/B00FLYWNYQ?tag=followrefer20-20",
                "image": "", "category": "kitchen", "asin": "B00FLYWNYQ",
                "features": [
                    "7-in-1 multi-cooker: pressure cooker, slow cooker, rice cooker, steamer, sauté pan, yogurt maker, and warmer",
                    "6-quart capacity — feeds 4-6 people",
                    "Cooks up to 70% faster than traditional cooking methods",
                    "Over 10 safety features including overheat protection and safe-locking lid",
                    "Dishwasher-safe lid, inner pot with stainless steel handles",
                    "Delay start up to 24 hours",
                ],
                "specs": {"Capacity": "6 Quart", "Wattage": "1000W", "Dimensions": "13.38 x 12.21 x 12.48 inches", "Weight": "11.8 pounds"},
            },
            {
                "title": "Lodge 12 Inch Pre-Seasoned Cast Iron Skillet",
                "price": "$34.90", "rating": "4.8 out of 5 stars",
                "link": "https://www.amazon.com/dp/B00G2XGC88?tag=followrefer20-20",
                "image": "", "category": "kitchen", "asin": "B00G2XGC88",
                "features": [
                    "Pre-seasoned with 100% natural vegetable oil — ready to use right out of the box",
                    "12-inch diameter — perfect for family-sized meals",
                    "Works on all heat sources: induction, oven, grill, campfire, and stovetop",
                    "Gets better with every use — seasoning builds up over time",
                    "Made in the USA since 1896",
                    "Can handle temperatures up to 500°F in oven",
                ],
                "specs": {"Diameter": "12 inches", "Weight": "8 pounds", "Material": "Cast Iron", "Made In": "USA"},
            },
        ],
        "electronics": [
            {
                "title": "Apple AirPods Pro (2nd Generation) with MagSafe Case",
                "price": "$189.00", "rating": "4.7 out of 5 stars",
                "link": "https://www.amazon.com/dp/B0BDHWDR12?tag=followrefer20-20",
                "image": "", "category": "electronics", "asin": "B0BDHWDR12",
                "features": [
                    "Active Noise Cancellation up to 2x more effective than the previous generation",
                    "Adaptive Transparency mode lets in outside sound while reducing loud environmental noise",
                    "Personalized Spatial Audio with dynamic head tracking",
                    "Up to 6 hours of listening time (30 hours total with MagSafe Charging Case)",
                    "H2 chip delivers smarter noise cancellation and audio performance",
                    "Touch control on each AirPod stem for volume, tracks, calls",
                    "IPX4 sweat and water resistance",
                ],
                "specs": {"Chip": "Apple H2", "Battery (AirPods)": "Up to 6 hours", "Battery (with case)": "Up to 30 hours", "Water Resistance": "IPX4", "Weight per earbud": "5.3 grams"},
            },
            {
                "title": "Anker 737 Power Bank (PowerCore 24K), 24000mAh",
                "price": "$79.99", "rating": "4.6 out of 5 stars",
                "link": "https://www.amazon.com/dp/B09VPHVD28?tag=followrefer20-20",
                "image": "", "category": "electronics", "asin": "B09VPHVD28",
                "features": [
                    "140W max output — charges MacBook Pro in about 1.7 hours",
                    "24,000mAh capacity — charges iPhone 14 up to 4.6 times",
                    "Smart digital display shows exact battery percentage and wattage",
                    "Charges 3 devices simultaneously (2 USB-C + 1 USB-A)",
                    "Can be recharged itself in just 1.5 hours with 140W input",
                ],
                "specs": {"Capacity": "24,000mAh", "Max Output": "140W", "Ports": "2x USB-C, 1x USB-A", "Weight": "1.43 pounds", "Dimensions": "6.4 x 2.9 x 1.5 inches"},
            },
        ],
        "beauty": [
            {
                "title": "CeraVe Moisturizing Cream, 19 oz",
                "price": "$19.99", "rating": "4.7 out of 5 stars",
                "link": "https://www.amazon.com/dp/B00TTD9BRC?tag=followrefer20-20",
                "image": "", "category": "beauty", "asin": "B00TTD9BRC",
                "features": [
                    "Developed with dermatologists — suitable for sensitive, dry, and eczema-prone skin",
                    "Contains 3 essential ceramides (1, 3, 6-II) that restore and maintain the skin's natural barrier",
                    "Hyaluronic acid helps retain skin's natural moisture",
                    "MVE patented technology releases moisturizers throughout the day",
                    "Fragrance-free, non-comedogenic, non-irritating",
                    "19 oz jar lasts months even with daily use",
                ],
                "specs": {"Size": "19 oz (538g)", "Skin Type": "Dry, Normal, Sensitive", "Key Ingredients": "Ceramides 1, 3, 6-II, Hyaluronic Acid", "Fragrance": "Free"},
            },
        ],
        "fitness": [
            {
                "title": "Hydro Flask 32 oz Wide Mouth Water Bottle",
                "price": "$44.95", "rating": "4.7 out of 5 stars",
                "link": "https://www.amazon.com/dp/B01ACAXEIQ?tag=followrefer20-20",
                "image": "", "category": "fitness", "asin": "B01ACAXEIQ",
                "features": [
                    "TempShield double-wall vacuum insulation keeps drinks cold up to 24 hours, hot up to 12 hours",
                    "32 oz capacity — enough water for long hikes or gym sessions",
                    "Wide mouth opening fits ice cubes and is easy to clean",
                    "18/8 pro-grade stainless steel — no flavor transfer",
                    "Powder coat finish provides a secure grip and resists scratching",
                    "Lifetime warranty",
                ],
                "specs": {"Capacity": "32 oz (946ml)", "Material": "18/8 Stainless Steel", "Cold": "Up to 24 hours", "Hot": "Up to 12 hours", "Weight": "0.44 lbs (200g)"},
            },
        ],
        "home": [
            {
                "title": "Bissell Little Green Portable Carpet and Upholstery Cleaner",
                "price": "$89.99", "rating": "4.5 out of 5 stars",
                "link": "https://www.amazon.com/dp/B0053QWOQ4?tag=followrefer20-20",
                "image": "", "category": "home", "asin": "B0053QWOQ4",
                "features": [
                    "Powerful suction removes tough stains from carpets, upholstery, car interiors",
                    "Sprays cleaning solution and suctions dirty water in one pass",
                    "48 oz clean water tank — enough for multiple spot cleanings",
                    "Includes tough stain tool, 3-inch stain tool, and 8 oz Bissell trial size formula",
                    "Compact size — 11 x 6 x 14 inches, easy to store in a closet",
                ],
                "specs": {"Tank Capacity": "48 oz", "Weight": "7.2 lbs", "Cord Length": "15 feet", "Dimensions": "11 x 6 x 14 inches"},
            },
        ],
        "baby": [
            {
                "title": "Frida Baby NoseFrida The Snotsucker Nasal Aspirator",
                "price": "$19.99", "rating": "4.7 out of 5 stars",
                "link": "https://www.amazon.com/dp/B00171WXII?tag=followrefer20-20",
                "image": "", "category": "baby", "asin": "B00171WXII",
                "features": [
                    "Doctor-recommended — used in Swedish hospitals",
                    "The filter prevents any mucus from reaching your mouth",
                    "More effective than bulb syringes — creates stronger, more controlled suction",
                    "Easy to use: place tip just inside nostril, put mouthpiece in your mouth, suck",
                    "Dishwasher safe — all parts except the filter can be washed",
                    "Works even when baby is fighting it — faster than traditional aspirators",
                ],
                "specs": {"Material": "BPA-free plastic", "Age Range": "0+ months", "Includes": "1 aspirator, 1 filter", "Dishwasher Safe": "Yes (except filter)"},
            },
        ],
        "pet-supplies": [
            {
                "title": "KONG Classic Dog Toy, Large",
                "price": "$13.99", "rating": "4.7 out of 5 stars",
                "link": "https://www.amazon.com/dp/B0002AR0I8?tag=followrefer20-20",
                "image": "", "category": "pet-supplies", "asin": "B0002AR0I8",
                "features": [
                    "Made from natural red rubber — virtually indestructible for power chewers",
                    "Unpredictable bounce keeps dogs entertained for hours",
                    "Stuff with treats or peanut butter to extend playtime",
                    "Can be frozen with stuffing for longer-lasting enrichment",
                    "Helps with separation anxiety and boredom",
                    "Veterinarian recommended for dental health",
                ],
                "specs": {"Size": "Large (fits dogs 30-65 lbs)", "Material": "Natural Rubber", "Dimensions": "4.5 inches tall", "Dishwasher Safe": "Yes"},
            },
        ],
    }
    data = fallbacks.get(category, fallbacks["kitchen"])
    return data[:count]
