import requests
import random
import re

UNSPLASH_CATEGORY_QUERIES = {
    "kitchen":      ["modern kitchen cooking", "kitchen tools minimal", "cooking food preparation"],
    "electronics":  ["technology gadgets minimal", "electronics modern", "tech workspace clean"],
    "beauty":       ["beauty skincare minimal", "cosmetics clean aesthetic", "skincare routine"],
    "fitness":      ["fitness workout minimal", "gym exercise healthy", "sport active lifestyle"],
    "home":         ["home interior minimal", "cozy home decor", "modern living room"],
    "outdoor":      ["outdoor nature adventure", "camping hiking nature", "outdoor lifestyle"],
    "baby":         ["baby nursery minimal", "cute baby items", "newborn essentials"],
    "pet-supplies": ["pet dog cat minimal", "cute pet lifestyle", "pet care"],
}

def get_unsplash_image(category: str) -> dict:
    """Unsplash에서 무료 이미지 가져오기 (API 키 불필요)"""
    try:
        queries = UNSPLASH_CATEGORY_QUERIES.get(category, ["product lifestyle minimal"])
        query = random.choice(queries).replace(" ", "-")
        
        # Unsplash Source API (무료, API 키 불필요)
        width, height = 1200, 630
        url = f"https://source.unsplash.com/featured/{width}x{height}/?{query}"
        
        resp = requests.head(url, allow_redirects=True, timeout=10)
        final_url = resp.url
        
        if "unsplash.com/photos" in final_url or "images.unsplash.com" in final_url:
            return {
                "url": final_url,
                "alt": query.replace("-", " ").title(),
                "credit": "Photo from Unsplash"
            }
    except Exception as e:
        print(f"  Unsplash 이미지 실패: {e}")
    
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
    
    # 아마존 상품 이미지 먼저 시도
    product_img = get_amazon_product_image(product)
    
    # Unsplash 분위기 이미지
    unsplash = get_unsplash_image(category)
    
    html = '<div class="fr-images">\n'
    
    # 분위기 이미지 (헤더)
    if unsplash:
        html += f'''  <div class="fr-hero-img">
    <img src="{unsplash['url']}" alt="{unsplash['alt']}" style="width:100%;height:360px;object-fit:cover;border-radius:16px;margin-bottom:24px;" loading="lazy">
  </div>\n'''
    
    # 상품 이미지
    if product_img:
        html += f'''  <div class="fr-product-img" style="text-align:center;margin:24px 0;">
    <img src="{product_img}" alt="{product.get('title', 'Product image')}" style="max-width:400px;max-height:400px;object-fit:contain;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);" loading="lazy">
  </div>\n'''
    
    html += '</div>\n'
    return html
