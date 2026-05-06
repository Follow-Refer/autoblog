import os
import random
from scraper import get_bestseller_products
from review_scraper import get_amazon_reviews
from content_generator import generate_post
from wordpress_poster import post_to_wordpress

def main():
    print("=== AutoBlog 시작 ===")

    categories = [
        "kitchen", "electronics", "beauty", "fitness",
        "home", "outdoor", "baby", "pet-supplies"
    ]
    category = random.choice(categories)
    print(f"오늘의 카테고리: {category}")

    products = get_bestseller_products(category, count=3)

    if not products:
        print("상품을 찾지 못했습니다.")
        return

    for i, product in enumerate(products):
        print(f"\n[{i+1}/3] 처리 중: {product['title'][:50]}...")

        # 실제 아마존 리뷰 가져오기
        print(f"  리뷰 수집 중...")
        reviews = get_amazon_reviews(product["link"])
        product["reviews"] = reviews

        if reviews["pros"]:
            print(f"  ✅ 장점 {len(reviews['pros'])}개, 단점 {len(reviews['cons'])}개 수집")
        else:
            print(f"  ⚠️ 리뷰 수집 실패 → AI가 자체 생성")

        # 한국어 포스트
        ko_post = generate_post(product, lang="ko")
        post_to_wordpress(ko_post, lang="ko")
        print(f"  ✅ 한국어 포스트 발행")

        # 영어 포스트
        en_post = generate_post(product, lang="en")
        post_to_wordpress(en_post, lang="en")
        print(f"  ✅ 영어 포스트 발행")

    print("\n=== AutoBlog 완료 ===")

if __name__ == "__main__":
    main()
