import os
import random
import time
from scraper import get_bestseller_products
from review_scraper import get_amazon_reviews
from content_generator import generate_post
from wordpress_poster import post_to_wordpress

# 스테디셀러 - 누구나 쓰는 일상용품
STEADY_SELLERS = [
    # 주방
    {"title": "Instant Pot Duo 7-in-1 Electric Pressure Cooker 6 Quart", "price": "$89.99", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B00FLYWNYQ?tag=followrefer20-20", "image": "", "category": "kitchen", "asin": "B00FLYWNYQ"},
    {"title": "Lodge 12 Inch Cast Iron Skillet", "price": "$34.90", "rating": "4.8 out of 5 stars", "link": "https://www.amazon.com/dp/B00G2XGC88?tag=followrefer20-20", "image": "", "category": "kitchen", "asin": "B00G2XGC88"},
    {"title": "OXO Good Grips 3-Piece Mixing Bowl Set", "price": "$28.99", "rating": "4.6 out of 5 stars", "link": "https://www.amazon.com/dp/B0000CFLJA?tag=followrefer20-20", "image": "", "category": "kitchen", "asin": "B0000CFLJA"},
    # 뷰티/스킨케어
    {"title": "CeraVe Moisturizing Cream 19 oz", "price": "$19.99", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B00TTD9BRC?tag=followrefer20-20", "image": "", "category": "beauty", "asin": "B00TTD9BRC"},
    {"title": "COSRX Advanced Snail 96 Mucin Power Essence", "price": "$19.99", "rating": "4.5 out of 5 stars", "link": "https://www.amazon.com/dp/B00PBX3L7K?tag=followrefer20-20", "image": "", "category": "beauty", "asin": "B00PBX3L7K"},
    {"title": "Neutrogena Hydro Boost Water Gel", "price": "$17.99", "rating": "4.5 out of 5 stars", "link": "https://www.amazon.com/dp/B00NR1YQHM?tag=followrefer20-20", "image": "", "category": "beauty", "asin": "B00NR1YQHM"},
    # 건강/피트니스
    {"title": "Hydro Flask 32 oz Water Bottle", "price": "$44.95", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B01ACAXEIQ?tag=followrefer20-20", "image": "", "category": "fitness", "asin": "B01ACAXEIQ"},
    {"title": "Fitbit Inspire 3 Health Fitness Tracker", "price": "$79.95", "rating": "4.4 out of 5 stars", "link": "https://www.amazon.com/dp/B09BKMFK7B?tag=followrefer20-20", "image": "", "category": "fitness", "asin": "B09BKMFK7B"},
    {"title": "Resistance Bands Set for Working Out", "price": "$29.99", "rating": "4.6 out of 5 stars", "link": "https://www.amazon.com/dp/B01AVDVHTI?tag=followrefer20-20", "image": "", "category": "fitness", "asin": "B01AVDVHTI"},
    # 집/생활
    {"title": "Roomba 694 Robot Vacuum", "price": "$179.99", "rating": "4.4 out of 5 stars", "link": "https://www.amazon.com/dp/B08379498P?tag=followrefer20-20", "image": "", "category": "home", "asin": "B08379498P"},
    {"title": "Command Picture Hanging Strips", "price": "$14.98", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B073XS3CHW?tag=followrefer20-20", "image": "", "category": "home", "asin": "B073XS3CHW"},
    {"title": "Bissell Little Green Portable Carpet Cleaner", "price": "$89.99", "rating": "4.5 out of 5 stars", "link": "https://www.amazon.com/dp/B0053QWOQ4?tag=followrefer20-20", "image": "", "category": "home", "asin": "B0053QWOQ4"},
    # 전자기기
    {"title": "Anker 737 Power Bank 24000mAh", "price": "$79.99", "rating": "4.6 out of 5 stars", "link": "https://www.amazon.com/dp/B09VPHVD28?tag=followrefer20-20", "image": "", "category": "electronics", "asin": "B09VPHVD28"},
    {"title": "Kindle Paperwhite E-reader", "price": "$139.99", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B08KTZ8249?tag=followrefer20-20", "image": "", "category": "electronics", "asin": "B08KTZ8249"},
    {"title": "Apple AirPods Pro 2nd Generation", "price": "$189.00", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B0BDHWDR12?tag=followrefer20-20", "image": "", "category": "electronics", "asin": "B0BDHWDR12"},
    # 반려동물
    {"title": "KONG Classic Dog Toy", "price": "$13.99", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B0002AR0I8?tag=followrefer20-20", "image": "", "category": "pet-supplies", "asin": "B0002AR0I8"},
    {"title": "Furminator Undercoat Deshedding Tool for Dogs", "price": "$29.99", "rating": "4.6 out of 5 stars", "link": "https://www.amazon.com/dp/B000SH0LQQ?tag=followrefer20-20", "image": "", "category": "pet-supplies", "asin": "B000SH0LQQ"},
    # 아기
    {"title": "Frida Baby NoseFrida Nasal Aspirator", "price": "$19.99", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B00171WXII?tag=followrefer20-20", "image": "", "category": "baby", "asin": "B00171WXII"},
    {"title": "Honest Company Baby Wipes", "price": "$16.99", "rating": "4.8 out of 5 stars", "link": "https://www.amazon.com/dp/B00K0MDNFI?tag=followrefer20-20", "image": "", "category": "baby", "asin": "B00K0MDNFI"},
    # 사무/문구
    {"title": "Post-it Notes 3x3 Inches 24 Pads", "price": "$14.99", "rating": "4.8 out of 5 stars", "link": "https://www.amazon.com/dp/B00006JNNO?tag=followrefer20-20", "image": "", "category": "home", "asin": "B00006JNNO"},
    {"title": "Pilot G2 Premium Retractable Gel Ink Pens", "price": "$12.99", "rating": "4.7 out of 5 stars", "link": "https://www.amazon.com/dp/B00006JNJ8?tag=followrefer20-20", "image": "", "category": "home", "asin": "B00006JNJ8"},
]

CATEGORIES = [
    "kitchen",
    "beauty",
    "fitness",
    "home",
    "baby",
    "pet-supplies",
]

def main():
    # 언어 설정 (환경변수에서 읽기, 기본값 en)
    lang = os.environ.get("BLOG_LANG", "en")
    print(f"=== AutoBlog Start (lang={lang}) ===")

    wait = random.randint(0, 1800)
    print(f"Waiting {wait//60} minutes...")
    time.sleep(wait)

    category = random.choice(CATEGORIES)

    roll = random.random()

    if roll < 0.25:
        product = random.choice(STEADY_SELLERS)
        products = [product]
        print(f"Today: Steady Seller - {product['title'][:40]}")
    elif roll < 0.35:
        products = get_bestseller_products("electronics", count=1)
        print("Today: Electronics Bestseller")
    else:
        products = get_bestseller_products(category, count=1)
        print(f"Today: {category} Bestseller")

    if not products:
        print("No products found.")
        return

    product = products[0]
    print(f"\nProcessing: {product['title'][:50]}...")

    print("  Collecting reviews...")
    reviews = get_amazon_reviews(product["link"])
    product["reviews"] = reviews

    if reviews["pros"]:
        print(f"  Reviews: {len(reviews['pros'])} pros, {len(reviews['cons'])} cons")
    else:
        print("  No reviews - AI will generate naturally")

    post = generate_post(product, lang=lang)
    result = post_to_wordpress(post, lang=lang)
    if result:
        print(f"  Published: {result.get('link', 'ok')}")

    print(f"\n=== AutoBlog Done (lang={lang}) ===")

if __name__ == "__main__":
    main()
