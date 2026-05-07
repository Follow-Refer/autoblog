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

    if random.random() < 0.3:
        products = get_bestseller_products("electronics", count=1)
        print("Today: Electronics")
    else:
        products = get_bestseller_products(category, count=1)
        print(f"Today: {category}")

    if not products:
        print("No products found.")
        return

    product = products[0]
    print(f"\nProcessing: {product['title'][:50]}...")

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
