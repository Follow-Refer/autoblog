import anthropic
import os
import random
import json
import re
from image_fetcher import build_image_html

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

AMAZON_ID = "followrefer20-20"

STYLES = {
    "en": [
        "honest and conversational, like a trusted friend who actually bought and used this",
        "detailed and specific, like someone who tested every feature thoroughly",
        "warm and practical, a busy parent sharing real-world experience with this product",
        "budget-conscious and direct, always focused on real value for money",
        "enthusiastic but fair, mentioning specific details only an owner would know",
    ],
    "es": [
        "honesto y conversacional, como un amigo de confianza que realmente lo compró y usó",
        "detallado y específico, como alguien que probó cada función a fondo",
        "cálido y práctico, un padre ocupado compartiendo experiencia real con este producto",
        "consciente del presupuesto, siempre enfocado en el valor real por el dinero",
        "entusiasta pero justo, mencionando detalles específicos que solo un dueño conocería",
    ],
    "in": [
        "ईमानदार और बातचीत वाला, जैसे किसी ऐसे दोस्त की बात जिसने सच में इसे खरीदा और इस्तेमाल किया",
        "विस्तृत और विशिष्ट, जैसे किसी ने हर फीचर को अच्छी तरह परखा हो",
        "गर्मजोशी से भरा और व्यावहारिक, एक व्यस्त माता-पिता की असली अनुभव वाली बात",
        "बजट के प्रति सचेत, हमेशा पैसे की असली कीमत पर ध्यान देने वाला",
        "उत्साही लेकिन निष्पक्ष, ऐसी बारीकियां बताने वाला जो सिर्फ मालिक ही जान सकता है",
    ],
    "kr": [
        "솔직하고 친근하게, 진짜로 구매해서 써본 친구가 얘기해주듯",
        "꼼꼼하고 구체적으로, 모든 기능을 직접 테스트해본 사람처럼",
        "따뜻하고 실용적으로, 바쁜 일상에서 실제 사용 경험을 나눠주듯",
        "가성비 중심으로, 돈 값어치를 철저히 따지는 스타일로",
        "열정적이지만 공정하게, 실제 사용자만 알 수 있는 디테일을 곁들여서",
    ],
}

LANG_CONFIG = {
    "en": {
        "write_in": "English",
        "buy_btn_text": "Check Price on Amazon →",
        "bottom_line": "Bottom Line",
        "verified": "based on verified buyers",
        "what_i_like": "What I like about it",
        "good_stuff": "✅ The good stuff",
        "worth_knowing": "❌ Worth knowing",
        "honest_take": "My honest take",
        "buy_if": "Buy this if you...",
        "skip_if": "Skip it if you...",
        "disclaimer": "📢 <strong>Affiliate Disclosure:</strong> This post contains affiliate links. If you purchase through them, I may earn a small commission at no extra cost to you.<br><br><strong>Disclaimer:</strong> Reviews are based on publicly available information and verified buyer feedback. Results may vary. Always check product details before purchasing.",
        "default_pros": "- Works exactly as described with no setup issues\n- Noticeably better than cheaper alternatives I've tried\n- Holds up well after months of regular use",
        "default_cons": "- Instructions could use more detail for advanced features\n- Packaging could be sturdier for shipping",
    },
    "es": {
        "write_in": "Spanish (Latin American)",
        "buy_btn_text": "Ver precio en Amazon →",
        "bottom_line": "Conclusión",
        "verified": "basado en compradores verificados",
        "what_i_like": "Lo que me gusta",
        "good_stuff": "✅ Lo bueno",
        "worth_knowing": "❌ Lo que debes saber",
        "honest_take": "Mi opinión honesta",
        "buy_if": "Cómpralo si...",
        "skip_if": "Evítalo si...",
        "disclaimer": "📢 <strong>Divulgación de afiliados:</strong> Esta publicación contiene enlaces de afiliados. Si compras a través de ellos, puedo ganar una pequeña comisión sin costo adicional para ti.<br><br><strong>Descargo de responsabilidad:</strong> Las reseñas se basan en información pública y comentarios de compradores verificados. Los resultados pueden variar.",
        "default_pros": "- Funciona exactamente como se describe sin problemas de configuración\n- Notablemente mejor que alternativas más baratas que he probado\n- Se mantiene bien después de meses de uso regular",
        "default_cons": "- Las instrucciones podrían tener más detalle para funciones avanzadas\n- El empaque podría ser más resistente para el envío",
    },
    "in": {
        "write_in": "Hindi",
        "buy_btn_text": "Amazon पर कीमत देखें →",
        "bottom_line": "निष्कर्ष",
        "verified": "verified खरीदारों के अनुसार",
        "what_i_like": "मुझे क्या पसंद आया",
        "good_stuff": "✅ अच्छी बातें",
        "worth_knowing": "❌ ध्यान देने योग्य बातें",
        "honest_take": "मेरी ईमानदार राय",
        "buy_if": "यह खरीदें अगर...",
        "skip_if": "इसे छोड़ें अगर...",
        "disclaimer": "📢 <strong>Affiliate Disclosure:</strong> इस पोस्ट में affiliate links हैं। खरीदारी पर मुझे कमीशन मिल सकता है, आपको कोई अतिरिक्त खर्च नहीं होगा।<br><br><strong>अस्वीकरण:</strong> समीक्षाएं सार्वजनिक जानकारी और verified खरीदारों के फीडबैक पर आधारित हैं। परिणाम अलग हो सकते हैं।",
        "default_pros": "- बिना किसी परेशानी के बिल्कुल वैसे काम करता है जैसा बताया गया\n- सस्ते विकल्पों से काफी बेहतर\n- महीनों के नियमित उपयोग के बाद भी मजबूत",
        "default_cons": "- उन्नत सुविधाओं के लिए निर्देश और विस्तृत हो सकते थे\n- शिपिंग के लिए पैकेजिंग और मजबूत हो सकती थी",
    },
    "kr": {
        "write_in": "Korean",
        "buy_btn_text": "아마존에서 가격 확인 →",
        "bottom_line": "한줄 요약",
        "verified": "구매자 리뷰 기반",
        "what_i_like": "마음에 드는 점",
        "good_stuff": "✅ 좋은 점",
        "worth_knowing": "❌ 알아두면 좋은 점",
        "honest_take": "솔직한 총평",
        "buy_if": "이런 분께 추천해요",
        "skip_if": "이런 분은 패스하세요",
        "disclaimer": "📢 <strong>제휴 공개:</strong> 이 포스팅에는 제휴 링크가 포함되어 있습니다. 링크를 통해 구매하시면 추가 비용 없이 소정의 수수료를 받을 수 있습니다.<br><br><strong>면책 조항:</strong> 리뷰는 공개된 정보와 구매자 피드백을 바탕으로 작성되었습니다. 개인에 따라 결과가 다를 수 있습니다.",
        "default_pros": "- 설명대로 아무 문제 없이 바로 작동함\n- 비슷한 가격대 제품들보다 확실히 나음\n- 몇 달 쓰고 있는데도 품질 유지됨",
        "default_cons": "- 고급 기능 설명이 좀 더 자세했으면 좋겠음\n- 배송용 포장이 좀 더 튼튼했으면 함",
    },
}

CSS = """<style>
.fr-review{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:740px;margin:0 auto;color:#1a1a1a;line-height:1.7}
.fr-summary-box{background:#f7f7f7;border-radius:14px;padding:24px 28px;margin:28px 0}
.fr-verdict{font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:6px}
.fr-one-line{font-size:18px;color:#111;margin:0;font-weight:500}
.fr-rating{display:flex;align-items:center;gap:8px;margin:18px 0}
.fr-stars{color:#f5a623;font-size:18px}
.fr-rating-text{font-size:14px;color:#666}
.fr-section{margin:32px 0}
.fr-section h2{font-size:20px;font-weight:600;margin-bottom:14px;color:#111}
.fr-pros-cons{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0}
@media(max-width:600px){.fr-pros-cons{grid-template-columns:1fr}}
.fr-pros{background:#f0faf4;border:1px solid #c6e8d1;border-radius:12px;padding:18px 20px}
.fr-cons{background:#fff5f5;border:1px solid #ffd0d0;border-radius:12px;padding:18px 20px}
.fr-pros h3{color:#1a7f4b;font-size:15px;margin:0 0 10px}
.fr-cons h3{color:#c0392b;font-size:15px;margin:0 0 10px}
.fr-pros ul,.fr-cons ul{margin:0;padding-left:18px;font-size:14.5px}
.fr-pros li,.fr-cons li{margin-bottom:6px}
.fr-who{background:#f0f4ff;border-radius:12px;padding:18px 22px;margin:20px 0;font-size:14.5px}
.fr-who strong{display:block;margin-bottom:8px;color:#2c3e7a;font-size:15px}
.fr-buy-btn{display:inline-block;background:#ff9900;color:#111!important;text-decoration:none;padding:14px 32px;border-radius:10px;font-weight:700;font-size:15px;margin:6px 0}
.fr-disclaimer{font-size:12px;color:#aaa;margin-top:28px;padding-top:16px;border-top:1px solid #eee}
p{font-size:15.5px;color:#333;margin-bottom:16px}
</style>"""

def make_amazon_link(product: dict) -> str:
    original = product.get("link", "")
    if "tag=" in original:
        return original
    sep = "&" if "?" in original else "?"
    return original + sep + "tag=" + AMAZON_ID

def generate_post(product: dict, lang: str = "en") -> dict:
    cfg   = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    style = random.choice(STYLES.get(lang, STYLES["en"]))
    link  = make_amazon_link(product)

    reviews  = product.get("reviews", {})
    features = product.get("features", [])
    specs    = product.get("specs", {})

    # 실제 리뷰 텍스트
    pros_raw = "\n".join("- " + r for r in reviews.get("pros", []))
    cons_raw = "\n".join("- " + r for r in reviews.get("cons", []))
    if not pros_raw:
        pros_raw = cfg["default_pros"]
    if not cons_raw:
        cons_raw = cfg["default_cons"]

    # 제품 특징 텍스트
    features_text = "\n".join("• " + f for f in features) if features else "Not available"

    # 스펙 텍스트
    specs_text = "\n".join(f"• {k}: {v}" for k, v in specs.items()) if specs else "Not available"

    buy_btn = (
        '<a href="' + link + '" class="fr-buy-btn" target="_blank" rel="nofollow sponsored">'
        + cfg["buy_btn_text"] + '</a>'
    )

    prompt = f"""You are a real person who bought this exact product and used it for months. Write an honest, specific, helpful review.

CRITICAL: Write the ENTIRE response in {cfg["write_in"]} only. Title, content, excerpt, tags — everything must be in {cfg["write_in"]}.

=== PRODUCT INFO (USE THESE EXACT DETAILS) ===
Product Name: {product['title']}
Price: {product['price']}
Rating: {product['rating']}
Category: {product['category']}

=== ACTUAL PRODUCT FEATURES (from Amazon listing) ===
{features_text}

=== TECHNICAL SPECS ===
{specs_text}

=== REAL BUYER REVIEWS ===
PROS (from verified buyers):
{pros_raw}

CONS (from verified buyers):
{cons_raw}

=== WRITING RULES ===
1. Write in {cfg["write_in"]} only — no other language
2. Style: {style}
3. MUST mention specific features, dimensions, real numbers from the product info above
4. NEVER make up features that aren't in the product info
5. Sound like a real human — use "I", personal experiences, casual phrases
6. Be specific: if it's a water bottle, mention "24-hour cold retention" not just "keeps drinks cold"
7. Title must include the ACTUAL product name and be SEO-optimized (under 65 chars)
8. Include both genuine praise AND honest criticism

Use exactly this HTML structure:
<div class="fr-review">
<div class="fr-summary-box"><p class="fr-verdict">{cfg["bottom_line"]}</p><p class="fr-one-line">One punchy honest sentence that mentions a specific feature</p></div>
<div class="fr-rating"><span class="fr-stars">⭐⭐⭐⭐⭐</span><span class="fr-rating-text">{product['rating']} — {cfg["verified"]}</span></div>
<p>Natural 2-3 sentence intro mentioning why you bought it and first impression</p>
<div class="fr-section"><h2>{cfg["what_i_like"]}</h2><p>2-3 paragraphs with SPECIFIC details from the features list. Mention real numbers, dimensions, actual performance.</p></div>
<div class="fr-pros-cons">
<div class="fr-pros"><h3>{cfg["good_stuff"]}</h3><ul><li>Specific pro with detail</li><li>Specific pro with detail</li><li>Specific pro with detail</li></ul></div>
<div class="fr-cons"><h3>{cfg["worth_knowing"]}</h3><ul><li>Specific con with detail</li><li>Specific con with detail</li></ul></div>
</div>
<div class="fr-section"><h2>{cfg["honest_take"]}</h2><p>2 paragraphs about real-world use. Who benefits most, any limitations.</p></div>
<div class="fr-who">
<strong>{cfg["buy_if"]}</strong><p>2-3 specific types of people who'd love this</p>
<strong>{cfg["skip_if"]}</strong><p>1-2 honest reasons someone might want something else</p>
</div>
<div class="fr-section">{buy_btn}</div>
<p class="fr-disclaimer">{cfg["disclaimer"]}</p>
</div>

Respond ONLY in valid JSON, no markdown, no explanation:
{{"title": "SEO title under 65 chars with actual product name", "content": "complete HTML", "excerpt": "summary under 160 chars", "tags": ["tag1","tag2","tag3","tag4","tag5"]}}"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw   = message.content[0].text.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data  = json.loads(match.group() if match else raw)

    image_html      = build_image_html(product)
    data["content"] = CSS + image_html + data["content"]
    data["product"] = product
    data["lang"]    = lang
    return data
