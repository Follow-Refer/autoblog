import anthropic
import os
import random
import json
import re
import hashlib
from image_fetcher import build_image_html
from link_checker import best_link

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-5"

# 정직한 방식: AI가 '직접 써봤다'고 지어내지 않고, 구매자 리뷰·스펙을 조사해 정리하는 에디터 시점.
# (미국 FTC 가짜 후기 규정 + 아마존 제휴 약관 + 구글 검색 품질 기준 모두 대응)

LANG_CONFIG = {
    "en": {
        "write_in": "English",
        "units": "US units (°F, inches, oz, lbs) are fine",
        "buy_btn": "Check Price on Amazon →",
        "bottom_line": "Bottom Line",
        "rating_note": "on Amazon",
        "love": "What buyers love",
        "gripes": "Common complaints",
        "good": "✅ Strengths",
        "bad": "❌ Watch out for",
        "take": "Our take",
        "buy_if": "Good fit if you...",
        "skip_if": "Look elsewhere if you...",
        "picks": "Our picks at a glance",
        "how": "How we chose",
        "disclaimer": "📢 <strong>Affiliate disclosure:</strong> We earn a small commission if you buy through our links, at no extra cost to you.<br><br><strong>How we review:</strong> We don't test every product in person. We research specs, manufacturer info and thousands of verified buyer reviews, then summarize what matters. Prices and availability change — check Amazon for current details.",
    },
    "es": {
        "write_in": "Latin American Spanish",
        "units": "metric only (°C, cm, ml, kg) — convert any imperial units",
        "buy_btn": "Ver precio en Amazon →",
        "bottom_line": "En resumen",
        "rating_note": "en Amazon",
        "love": "Lo que más valoran los compradores",
        "gripes": "Quejas frecuentes",
        "good": "✅ Puntos fuertes",
        "bad": "❌ A tener en cuenta",
        "take": "Nuestra opinión",
        "buy_if": "Te conviene si...",
        "skip_if": "Mejor busca otra opción si...",
        "picks": "Nuestras recomendaciones",
        "how": "Cómo elegimos",
        "disclaimer": "📢 <strong>Divulgación:</strong> Ganamos una pequeña comisión si compras a través de nuestros enlaces, sin costo extra para ti.<br><br><strong>Cómo reseñamos:</strong> No probamos cada producto en persona. Investigamos especificaciones, información del fabricante y miles de opiniones de compradores verificados, y resumimos lo importante. Precios y disponibilidad cambian — revisa Amazon.",
    },
    "in": {
        "write_in": "Brazilian Portuguese",
        "units": "metric only (°C, cm, ml, kg) — convert any imperial units",
        "buy_btn": "Ver preço na Amazon →",
        "bottom_line": "Resumo",
        "rating_note": "na Amazon",
        "love": "O que os compradores mais elogiam",
        "gripes": "Reclamações comuns",
        "good": "✅ Pontos fortes",
        "bad": "❌ Fique atento",
        "take": "Nossa opinião",
        "buy_if": "Vale a pena se você...",
        "skip_if": "Procure outra opção se você...",
        "picks": "Nossas escolhas",
        "how": "Como escolhemos",
        "disclaimer": "📢 <strong>Divulgação:</strong> Ganhamos uma pequena comissão se você comprar pelos nossos links, sem custo extra.<br><br><strong>Como avaliamos:</strong> Não testamos cada produto pessoalmente. Pesquisamos especificações e milhares de avaliações de compradores verificados e resumimos o essencial.",
    },
    "kr": {
        "write_in": "Korean",
        "units": "미터법만 사용 (°C, cm, ml, kg)",
        "buy_btn": "아마존에서 가격 확인 →",
        "bottom_line": "한줄 요약",
        "rating_note": "아마존 기준",
        "love": "구매자들이 좋아하는 점",
        "gripes": "자주 나오는 불만",
        "good": "✅ 장점",
        "bad": "❌ 주의할 점",
        "take": "종합 의견",
        "buy_if": "이런 분께 맞아요",
        "skip_if": "이런 분은 다른 제품을",
        "picks": "한눈에 보는 추천",
        "how": "고른 기준",
        "disclaimer": "📢 <strong>제휴 공개:</strong> 링크를 통해 구매하시면 추가 비용 없이 소정의 수수료를 받습니다.<br><br><strong>리뷰 방식:</strong> 모든 제품을 직접 써보지는 않습니다. 스펙과 수천 건의 구매자 리뷰를 조사해 핵심만 정리합니다.",
    },
}

HONESTY_RULES = """HONESTY RULES (strict):
- You are an editor who RESEARCHED this product. You did NOT buy or use it.
- Never write "I bought", "I've used", "after 4 months", "my kitchen", or any invented personal experience.
- Attribute experiences to buyers: "buyers say", "many reviewers mention", "a common complaint is".
- Only state specs/features given below. If a detail is not given, don't invent it.
- Translate specs into everyday meaning (e.g. "24h cold" -> "still icy after a full workday").
"""

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
.fr-buy-btn.coupang{background:#e8343b;color:#fff!important;}
.fr-disclaimer{font-size:12px;color:#aaa;margin-top:28px;padding-top:16px;border-top:1px solid #eee}
p{font-size:15.5px;color:#333;margin-bottom:16px}
</style>"""


def _call(prompt: str, max_tokens: int = 4000) -> dict:
    msg = client.messages.create(model=MODEL, max_tokens=max_tokens,
                                 messages=[{"role": "user", "content": prompt}])
    raw = msg.content[0].text.strip()
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    return json.loads(m.group() if m else raw)


def _btn(link: str, cfg: dict) -> str:
    return f'<a href="{link}" class="fr-buy-btn" target="_blank" rel="nofollow sponsored">{cfg["buy_btn"]}</a>'


def _facts(p: dict) -> str:
    feats = "\n".join("- " + f for f in p.get("features", [])) or "- (none listed)"
    specs = "\n".join(f"- {k}: {v}" for k, v in p.get("specs", {}).items())
    rv = p.get("reviews", {}) or {}
    pros = "\n".join("- " + r for r in rv.get("pros", [])) or "- (no scraped reviews; rely on features)"
    cons = "\n".join("- " + r for r in rv.get("cons", [])) or "- (no scraped complaints; mention typical trade-offs cautiously)"
    return (f"Name: {p['title']}\nPrice (approx.): {p.get('price','')}\nRating: {p.get('rating','')}\n"
            f"Features:\n{feats}\n{('Specs:' + chr(10) + specs) if specs else ''}\n"
            f"Buyer praise:\n{pros}\nBuyer complaints:\n{cons}")


JSON_TAIL = ('Respond ONLY with valid JSON, no markdown:\n'
             '{"title": "...", "content": "complete HTML", "excerpt": "under 155 chars", '
             '"tags": ["t1","t2","t3","t4","t5"]}')


def generate_post(product: dict, lang: str = "en") -> dict:
    """단일 상품 리뷰 (구매자 리뷰 종합형)."""
    cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    link = best_link(product)
    prompt = f"""Write a buyer's-guide style product review for a shopping blog.
Language: {cfg["write_in"]} ONLY (title, content, excerpt, tags). Units: {cfg["units"]}.

{HONESTY_RULES}
=== PRODUCT ===
{_facts(product)}

Title: include the real product name + a search-intent phrase (e.g. "review", "worth it?", "pros and cons"), under 65 chars. No fake time claims.

Use exactly this HTML (fill the placeholders, keep classes):
<div class="fr-review">
<div class="fr-summary-box"><p class="fr-verdict">{cfg["bottom_line"]}</p><p class="fr-one-line">one clear sentence: who it's for and why</p></div>
<div class="fr-rating"><span class="fr-stars">⭐⭐⭐⭐⭐</span><span class="fr-rating-text">{product.get('rating','')} {cfg["rating_note"]}</span></div>
<p>2-3 sentence intro: what problem this product solves and who searches for it</p>
<div class="fr-section"><h2>{cfg["love"]}</h2><p>2-3 paragraphs grounded in the features and buyer praise above</p></div>
<div class="fr-section"><h2>{cfg["gripes"]}</h2><p>1-2 paragraphs on real downsides from buyer complaints</p></div>
<div class="fr-pros-cons">
<div class="fr-pros"><h3>{cfg["good"]}</h3><ul><li>...</li><li>...</li><li>...</li></ul></div>
<div class="fr-cons"><h3>{cfg["bad"]}</h3><ul><li>...</li><li>...</li></ul></div>
</div>
<div class="fr-section"><h2>{cfg["take"]}</h2><p>1-2 paragraphs, balanced, practical</p></div>
<div class="fr-who"><strong>{cfg["buy_if"]}</strong><p>...</p><strong>{cfg["skip_if"]}</strong><p>...</p></div>
<div class="fr-section">{_btn(link, cfg)}</div>
<p class="fr-disclaimer">{cfg["disclaimer"]}</p>
</div>

{JSON_TAIL}"""
    data = _call(prompt)
    data["content"] = CSS + build_image_html(product) + data["content"]
    data["product"] = product
    data["lang"] = lang
    return data


def generate_guide(products: list, category: str, lang: str = "en") -> dict:
    """비교 추천글 (예: 'Best skincare picks under $30') — 검색 유입이 가장 잘 되는 형식."""
    cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    blocks = []
    for i, p in enumerate(products, 1):
        blocks.append(f"--- PRODUCT {i} ---\n{_facts(p)}\nBUY BUTTON HTML (copy exactly): {_btn(best_link(p), cfg)}")
    prompt = f"""Write a "best {category} products" comparison guide for a shopping blog, covering these {len(products)} products.
Language: {cfg["write_in"]} ONLY. Units: {cfg["units"]}.

{HONESTY_RULES}
{chr(10).join(blocks)}

Structure (keep classes):
<div class="fr-review">
<div class="fr-summary-box"><p class="fr-verdict">{cfg["picks"]}</p><p class="fr-one-line">one line naming the best overall and the best budget pick</p></div>
<p>short intro: what to look for when buying this type of product</p>
For each product: <div class="fr-section"><h2>N. Product name — best for X</h2><p>2 paragraphs from facts + buyer feedback</p><div class="fr-pros-cons"><div class="fr-pros"><h3>{cfg["good"]}</h3><ul>..</ul></div><div class="fr-cons"><h3>{cfg["bad"]}</h3><ul>..</ul></div></div>BUY BUTTON HTML</div>
<div class="fr-section"><h2>{cfg["how"]}</h2><p>explain criteria honestly (ratings, buyer reviews, price, specs — not hands-on testing)</p></div>
<p class="fr-disclaimer">{cfg["disclaimer"]}</p>
</div>

Title: search-intent style like "Best ... in 2026" / "Top 3 ... for ...", under 65 chars.
{JSON_TAIL}"""
    data = _call(prompt, max_tokens=6000)
    data["content"] = CSS + build_image_html(products[0]) + data["content"]
    key = "-".join(sorted(p.get("asin", "") for p in products))
    data["product"] = {"asin": "guide" + hashlib.md5(key.encode()).hexdigest()[:8], "category": category,
                       "title": products[0]["title"]}
    data["lang"] = lang
    return data
