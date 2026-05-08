import requests
import random
import hashlib

# 카테고리별 Picsum 시드 (일관된 이미지)
CATEGORY_SEEDS = {
    "kitchen":      ["kitchen", "cooking", "food", "chef", "recipe"],
    "electronics":  ["tech", "gadget", "digital", "device", "modern"],
    "beauty":       ["beauty", "skincare", "cosmetic", "glow", "spa"],
    "fitness":      ["fitness", "workout", "sport", "gym", "health"],
    "home":         ["home", "interior", "decor", "living", "cozy"],
    "outdoor":      ["outdoor", "nature", "adventure", "hiking", "travel"],
    "baby":         ["baby", "nursery", "kids", "infant", "family"],
    "pet-supplies": ["pet", "dog", "cat", "animal", "cute"],
}

def get_hero_image(category: str, title: str = "") -> dict:
    """picsum.photos에서 카테고리별 이미지 가져오기 (API 키 불필요)"""
    try:
        seeds = CATEGORY_SEEDS.get(category, ["product", "lifestyle", "minimal"])
        seed = random.choice(seeds)
        if title:
            # 제목 기반 시드로 일관된 이미지
            seed = hashlib.md5(title.encode()).hexdigest()[:8]

        url = f"https://picsum.photos/seed/{seed}/1200/630"

        resp = requests.head(url, allow_redirects=True, timeout=10)
        if resp.status_code == 200:
            return {
                "url": resp.url,
                "alt": category.replace("-", " ").title() + " lifestyle",
                "credit": "Photo from Picsum"
            }
    except Exception as e:
        print(f"  Hero image 실패: {e}")
    return None

def get_amazon_product_image(product: dict) -> str:
    """아마존 상품 이미지 URL 가져오기"""
    image = product.get("image", "")
    if image and image.startswith("http"):
        return image
    return None

def build_image_html(product: dict) -> str:
    """글 상단 이미지 HTML 생성"""
    category = product.get("category", "home")
    title    = product.get("title", "")

    hero        = get_hero_image(category, title)
    product_img = get_amazon_product_image(product)

    html = '<div class="fr-images">\n'

    if hero:
        html += f'''  <div class="fr-hero-img">
    <img src="{hero['url']}" alt="{hero['alt']}" style="width:100%;height:360px;object-fit:cover;border-radius:16px;margin-bottom:24px;" loading="lazy">
  </div>\n'''

    if product_img:
        html += f'''  <div class="fr-product-img" style="text-align:center;margin:24px 0;">
    <img src="{product_img}" alt="{title}" style="max-width:400px;max-height:400px;object-fit:contain;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);" loading="lazy">
  </div>\n'''

    html += '</div>\n'
    return html
