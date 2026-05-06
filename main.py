import os
import random
from scraper import get_bestseller_products
from content_generator import generate_post
from wordpress_poster import post_to_wordpress

def main():
    print("=== AutoBlog 시작 ===")
    
    # 카테고리 랜덤 선택 (매번 다른 카테고리)
    categories = [
        "kitchen", "electronics", "beauty", "fitness",
        "home", "outdoor", "baby", "pet-supplies"
    ]
    category = random.choice(categories)
    print(f"오늘의 카테고리: {category}")

    # 상품 3개 가져오기
    products = get_bestseller_products(category, count=3)
    
    if not products:
        print("상품을 찾지 못했습니다.")
        return

    for i, product in enumerate(products):
        print(f"\n[{i+1}/3] 글 생성 중: {product['title'][:50]}...")
        
        # 한국어 포스트 생성 및 발행
        ko_post = generate_post(product, lang="ko")
        post_to_wordpress(ko_post, lang="ko")
        print(f"  ✅ 한국어 포스트 발행 완료")

        # 영어 포스트 생성 및 발행
        en_post = generate_post(product, lang="en")
        post_to_wordpress(en_post, lang="en")
        print(f"  ✅ 영어 포스트 발행 완료")

    print("\n=== AutoBlog 완료 ===")

if __name__ == "__main__":
    main()
