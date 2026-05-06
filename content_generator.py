import anthropic
import os
import random

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

AMAZON_ID = "followrefer20-20"

STYLES = [
    "honest and conversational, like a trusted friend recommending something",
    "detailed and analytical, like a tech-savvy professional who tested it thoroughly",
    "warm and practical, a busy parent sharing what actually works at home",
    "budget-conscious and straightforward, always asking is it worth the money",
    "enthusiastic but fair, a hobbyist who loves trying new products",
]

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

EN_DEFAULT_PROS = "- Easy to use right out of the box\n- Great build quality for the price\n- Does exactly what it promises"
EN_DEFAULT_CONS = "- Instructions could be clearer\n- Packaging was a bit flimsy"

def make_amazon_link(product: dict) -> str:
    original = product.get("link", "")
    sep = "&" if "?" in original else "?"
    if "amazon.com" in original:
        return original + sep + "tag=" + AMAZON_ID
    return original

def generate_post(product: dict, lang: str = "en") -> dict:
    style   = random.choice(STYLES)
    link    = make_amazon_link(product)
    reviews = product.get("reviews", {})

    pros_raw = "\n".join("- " + r for r in reviews.get("pros", []))
    cons_raw = "\n".join("- " + r for r in reviews.get("cons", []))

    if not pros_raw:
        pros_raw = EN_DEFAULT_PROS
    if not cons_raw:
        cons_raw = EN_DEFAULT_CONS

    buy_btn = '<a href="' + link + '" class="fr-buy-btn" target="_blank" rel="nofollow sponsored">Check Price on Amazon →</a>'

    json_format = '{"title": "SEO title under 65 chars", "content": "complete HTML", "excerpt": "summary under 160 chars", "tags": ["tag1","tag2","tag3","tag4","tag5"]}'

    prompt = (
        "You are a real person who bought and used this product. Write an honest, helpful blog review.\n\n"
        "Product: " + product['title'] + "\n"
        "Price: " + product['price'] + "\n"
        "Rating: " + product['rating'] + "\n"
        "Category: " + product['category'] + "\n\n"
        "Real buyer feedback:\n"
        "PROS:\n" + pros_raw + "\n"
        "CONS:\n" + cons_raw + "\n\n"
        "Your writing style: " + style + "\n\n"
        "Rules:\n"
        "- Sound like a real human, not AI. Use casual phrases, personal opinions, occasional imperfections.\n"
        "- Be specific. Mention details that only someone who used it would know.\n"
        "- Include the cons honestly. Readers trust reviewers who admit flaws.\n"
        "- Title must be SEO-optimized but sound natural (under 65 chars).\n\n"
        "Use exactly this HTML structure:\n"
        '<div class="fr-review">\n'
        '<div class="fr-summary-box"><p class="fr-verdict">Bottom Line</p><p class="fr-one-line">Write one punchy honest sentence here</p></div>\n'
        '<div class="fr-rating"><span class="fr-stars">⭐⭐⭐⭐⭐</span><span class="fr-rating-text">' + product['rating'] + ' — based on verified buyers</span></div>\n'
        '<p>Write a natural 2-3 sentence intro here</p>\n'
        '<div class="fr-section"><h2>What I like about it</h2><p>Write 2-3 paragraphs based on the pros above. Be specific and conversational.</p></div>\n'
        '<div class="fr-pros-cons">\n'
        '<div class="fr-pros"><h3>✅ The good stuff</h3><ul><li>pro 1</li><li>pro 2</li><li>pro 3</li></ul></div>\n'
        '<div class="fr-cons"><h3>❌ Worth knowing</h3><ul><li>con 1 — honest and specific</li><li>con 2 — honest and specific</li></ul></div>\n'
        '</div>\n'
        '<div class="fr-section"><h2>My honest take</h2><p>Write 2 paragraphs: first about who this is perfect for, then about who might want to skip it. Be direct.</p></div>\n'
        '<div class="fr-who">\n'
        '<strong>Buy this if you...</strong><p>2-3 specific use cases</p>\n'
        '<strong>Skip it if you...</strong><p>1-2 honest reasons to pass</p>\n'
        '</div>\n'
        '<div class="fr-section">' + buy_btn + '</div>\n'
        '<p class="fr-disclaimer">This post contains affiliate links. If you buy through them, I may earn a small commission at no extra cost to you. I only recommend products I genuinely think are worth it.</p>\n'
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
    data["content"] = CSS + data["content"]
    data["product"] = product
    data["lang"]    = "en"
    return data
