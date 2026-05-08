import anthropic
import os
import random
from image_fetcher import build_image_html

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

AMAZON_ID = "followrefer20-20"

STYLES = {
    "en": [
        "honest and conversational, like a trusted friend recommending something",
        "detailed and analytical, like a tech-savvy professional who tested it thoroughly",
        "warm and practical, a busy parent sharing what actually works at home",
        "budget-conscious and straightforward, always asking is it worth the money",
        "enthusiastic but fair, a hobbyist who loves trying new products",
    ],
    "es": [
        "honesto y conversacional, como un amigo de confianza que recomienda algo",
        "detallado y analítico, como un profesional que lo probó a fondo",
        "cálido y práctico, un padre ocupado que comparte lo que realmente funciona",
        "consciente del presupuesto, siempre preguntando si vale la pena el dinero",
        "entusiasta pero justo, un aficionado que ama probar nuevos productos",
    ],
    "in": [
        "ईमानदार और बातचीत वाला, जैसे एक भरोसेमंद दोस्त कुछ सुझा रहा हो",
        "विस्तृत और विश्लेषणात्मक, जैसे किसी तकनीकी विशेषज्ञ ने इसे अच्छी तरह परखा हो",
        "गर्मजोशी से भरा और व्यावहारिक, एक व्यस्त माता-पिता जो घर में काम आने वाली चीजें बताते हैं",
        "बजट के प्रति सचेत, हमेशा यह पूछते हुए कि क्या यह पैसे के लायक है",
        "उत्साही लेकिन निष्पक्ष, एक शौकीन जो नए उत्पाद आजमाना पसंद करता है",
    ],
    "kr": [
        "솔직하고 친근한 말투로, 믿을 수 있는 친구가 추천해주는 것처럼",
        "꼼꼼하고 분석적으로, 직접 테스트해본 전문가처럼",
        "따뜻하고 실용적으로, 바쁜 부모가 실제로 효과 있는 것을 공유하듯",
        "가성비를 따지는 솔직한 스타일로, 돈 값어치가 있는지 항상 체크하는",
        "열정적이지만 공정하게, 새 제품 써보기 좋아하는 리뷰어처럼",
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
        "disclaimer": "📢 <strong>Affiliate Disclosure:</strong> This post contains affiliate links. If you purchase through them, I may earn a small commission at no extra cost to you.<br><br><strong>Disclaimer:</strong> The reviews on this site are based on publicly available information and user feedback. Results may vary by individual. We are not responsible for any adverse reactions or dissatisfaction resulting from products purchased through our links. Always read product labels carefully and consult a professional if needed. Purchase decisions are solely your own responsibility.",
        "default_pros": "- Easy to use right out of the box\n- Great build quality for the price\n- Does exactly what it promises",
        "default_cons": "- Instructions could be clearer\n- Packaging was a bit flimsy",
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
        "disclaimer": "📢 <strong>Divulgación de afiliados:</strong> Esta publicación contiene enlaces de afiliados. Si compras a través de ellos, puedo ganar una pequeña comisión sin costo adicional para ti.<br><br><strong>Descargo de responsabilidad:</strong> Las reseñas de este sitio se basan en información pública y comentarios de usuarios. Los resultados pueden variar. No somos responsables de ningún problema derivado de los productos comprados a través de nuestros enlaces. Lea siempre las etiquetas y consulte a un profesional si es necesario.",
        "default_pros": "- Fácil de usar desde el primer momento\n- Excelente calidad de construcción para el precio\n- Hace exactamente lo que promete",
        "default_cons": "- Las instrucciones podrían ser más claras\n- El embalaje era un poco frágil",
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
        "disclaimer": "📢 <strong>Affiliate Disclosure:</strong> इस पोस्ट में affiliate links हैं। अगर आप इनके जरिए खरीदारी करते हैं, तो मुझे एक छोटा कमीशन मिल सकता है, आपको कोई अतिरिक्त खर्च नहीं होगा।<br><br><strong>अस्वीकरण:</strong> इस साइट की समीक्षाएं सार्वजनिक जानकारी और उपयोगकर्ता फीडबैक पर आधारित हैं। परिणाम अलग-अलग हो सकते हैं। हम किसी भी समस्या के लिए जिम्मेदार नहीं हैं। हमेशा लेबल पढ़ें और जरूरत पड़ने पर विशेषज्ञ से सलाह लें।",
        "default_pros": "- पहली बार में ही आसानी से उपयोग\n- कीमत के हिसाब से बेहतरीन गुणवत्ता\n- जो वादा किया वही करता है",
        "default_cons": "- निर्देश और स्पष्ट हो सकते थे\n- पैकेजिंग थोड़ी कमजोर थी",
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
        "disclaimer": "📢 <strong>제휴 공개:</strong> 이 포스팅에는 제휴 링크가 포함되어 있습니다. 링크를 통해 구매하시면 추가 비용 없이 소정의 수수료를 받을 수 있습니다.<br><br><strong>면책 조항:</strong> 본 사이트의 리뷰는 공개된 정보와 구매자 피드백을 바탕으로 작성되었습니다. 개인에 따라 결과가 다를 수 있습니다. 링크를 통해 구매한 제품으로 인한 불만족에 대해 책임지지 않습니다. 항상 제품 라벨을 꼼꼼히 확인하시고, 필요시 전문가와 상담하세요.",
        "default_pros": "- 처음 사용해도 쉽고 간단함\n- 가격 대비 품질이 훌륭함\n- 제품 설명과 실제가 일치함",
        "default_cons": "- 설명서가 좀 더 자세했으면 좋겠음\n- 포장이 약간 허술한 편",
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
    sep = "&" if "?" in original else "?"
    if "amazon.com" in original:
        return original + sep + "tag=" + AMAZON_ID
    return original

def generate_post(product: dict, lang: str = "en") -> dict:
    cfg     = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    style   = random.choice(STYLES.get(lang, STYLES["en"]))
    link    = make_amazon_link(product)
    reviews = product.get("reviews", {})

    pros_raw = "\n".join("- " + r for r in reviews.get("pros", []))
    cons_raw = "\n".join("- " + r for r in reviews.get("cons", []))

    if not pros_raw:
        pros_raw = cfg["default_pros"]
    if not cons_raw:
        cons_raw = cfg["default_cons"]

    buy_btn = (
        '<a href="' + link + '" class="fr-buy-btn" target="_blank" rel="nofollow sponsored">'
        + cfg["buy_btn_text"] + '</a>'
    )

    json_format = '{"title": "SEO title under 65 chars", "content": "complete HTML", "excerpt": "summary under 160 chars", "tags": ["tag1","tag2","tag3","tag4","tag5"]}'

    prompt = (
        "You are a real person who bought and used this product. Write an honest, helpful blog review.\n"
        "IMPORTANT: Write the ENTIRE response in " + cfg["write_in"] + " only. Title, content, excerpt, tags — everything in " + cfg["write_in"] + ".\n\n"
        "Product: " + product['title'] + "\n"
        "Price: " + product['price'] + "\n"
        "Rating: " + product['rating'] + "\n"
        "Category: " + product['category'] + "\n\n"
        "Real buyer feedback:\n"
        "PROS:\n" + pros_raw + "\n"
        "CONS:\n" + cons_raw + "\n\n"
        "Your writing style: " + style + "\n\n"
        "Rules:\n"
        "- Sound like a real human, not AI.\n"
        "- Be specific. Mention details that only someone who used it would know.\n"
        "- Include the cons honestly.\n"
        "- Title must be SEO-optimized but sound natural (under 65 chars).\n\n"
        "Use exactly this HTML structure:\n"
        '<div class="fr-review">\n'
        '<div class="fr-summary-box"><p class="fr-verdict">' + cfg["bottom_line"] + '</p><p class="fr-one-line">one punchy sentence</p></div>\n'
        '<div class="fr-rating"><span class="fr-stars">⭐⭐⭐⭐⭐</span><span class="fr-rating-text">' + product['rating'] + ' — ' + cfg["verified"] + '</span></div>\n'
        '<p>2-3 sentence intro</p>\n'
        '<div class="fr-section"><h2>' + cfg["what_i_like"] + '</h2><p>2-3 paragraphs</p></div>\n'
        '<div class="fr-pros-cons">\n'
        '<div class="fr-pros"><h3>' + cfg["good_stuff"] + '</h3><ul><li>pro 1</li><li>pro 2</li><li>pro 3</li></ul></div>\n'
        '<div class="fr-cons"><h3>' + cfg["worth_knowing"] + '</h3><ul><li>con 1</li><li>con 2</li></ul></div>\n'
        '</div>\n'
        '<div class="fr-section"><h2>' + cfg["honest_take"] + '</h2><p>2 paragraphs</p></div>\n'
        '<div class="fr-who">\n'
        '<strong>' + cfg["buy_if"] + '</strong><p>2-3 use cases</p>\n'
        '<strong>' + cfg["skip_if"] + '</strong><p>1-2 reasons</p>\n'
        '</div>\n'
        '<div class="fr-section">' + buy_btn + '</div>\n'
        '<p class="fr-disclaimer">' + cfg["disclaimer"] + '</p>\n'
        '</div>\n\n'
        "Respond ONLY in valid JSON (no markdown, no explanation):\n" + json_format
    )

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json, re
    raw   = message.content[0].text.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data  = json.loads(match.group() if match else raw)

    image_html = build_image_html(product)
    data["content"] = CSS + image_html + data["content"]
    data["product"] = product
    data["lang"]    = lang
    return data
