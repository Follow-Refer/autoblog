import os
import random
import time
from scraper import get_bestseller_products
from review_scraper import get_amazon_reviews
from content_generator import generate_post
from wordpress_poster import post_to_wordpress

def main():
    wait = random.randint(0, 1800)
    print(f"Waiting {wait//60} minutes...")
    time.sleep(wait)
    
    print("=== AutoBlog Start ===")
    categories = [
        "kitchen", "beauty", "fitness",
        "home", "outdoor", "baby", "pet-supplies"
    ]
    category = random.choice(categories)
    print(f"Today's category: {category}")
    elec = get_bestseller_products("electronics", count=1)
    others = get_bestseller_products(category, count=2)
    products = elec + others
    if not products:
        print("No products found.")
        return
    for i, product in enumerate(products):
        print(f"\n[{i+1}/3] Processing: {product['title'][:50]}...")
        print("  Collecting reviews...")
        reviews = get_amazon_reviews(product["link"])
        product["reviews"] = reviews
        if reviews["pros"]:
            print(f"  Reviews collected: {len(reviews['pros'])} pros, {len(reviews['cons'])} cons")
        else:
            print("  No reviews found - AI will generate naturally")
        post = generate_post(product, lang="en")
        result = post_to_wordpress(post, lang="en")
        if result:
            print(f"  Published: {result.get('link', 'ok')}")
    print("\n=== AutoBlog Done ===")

if __name__ == "__main__":
    main()
