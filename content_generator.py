import anthropic
import os
import random

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

COUPANG_ID = "AF3726748"
AMAZON_ID  = "followrefer20-20"

KO_STYLES = [
    "솔직하고 친근한 이웃 느낌으로, 본인이 실제로 써본 것처럼",
    "꼼꼼하게 따져보는 성격의 30대 직장인 느낌으로",
    "생활용품에 진심인 주부 느낌으로, 실용성 중심으로",
    "가성비를 중요시하는 대학생 느낌으로, 솔직하게",
    "제품 리뷰를 즐기는 취미를 가진 사람 느낌으로",
]

EN_STYLES = [
    "honest and conversational, like a friend recommending something",
    "detailed and analytical, like a tech-savvy professional",
    "warm and practical, focusing on everyday usability",
    "budget-conscious and straightforward",
    "enthusiastic but balanced, mentioning both pros and cons",
]

CSS = """<style>
.fr-review{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:740px;margin:0 auto;color:#1a1a1a;line-height:1.7}
.fr-summary-box{background:#f7f7f7;border-radius:14px;padding:24px 28px;margin:28px 0}
.fr-verdict{font-size:15px;font-weight:600;margin-bottom:6px;color:#111}
.fr-one-line{font-size:17px;color:#333;margin:0}
.fr-rating{display:flex;align-items:center;gap:8px;margin:18px 0}
.fr-stars{color:#f5a623;font-size:18px}
.fr-rating-text{font-size:14px;color:#666}
.fr-section{margin:32px 0}
.fr-section h2{font-size:19px;font-weight:600;margin-bottom:14px;color:#111}
.fr-pros-cons{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0}
@media(max-width:600px){.fr-pros-cons{grid-template-columns:1fr}}
.fr-pros{background:#f0faf4;border:1px solid #c6e8d1;border-radius:12px;padding:18px 20px}
.fr-cons{background:#fff5f5;border:1px solid #ffd0d0;border-radius:12px;padding:18px 20px}
.fr-pros h3{color:#1a7f4b;font-size:15px;margin:0 0 10px}
.fr-cons h3{color:#c0392b;font-size:15px;margin:0 0 10px}
.fr-pros ul,.fr-cons ul{margin:0;padding-left:18px;font-size:14.5px}
.fr-pros li,.fr-cons li{margin-bottom:6px}
.fr-who{background:#f0f4ff;border-radius:12px;padding:18px 22px;margin:20px 0;font-size:14.5px}
.fr-who strong{display:block;margin-bottom:8px;color:#2c3e7a}
.fr-buy-btn{display:inline-block;background:#fe6600;color:#fff!important;text-decoration:none;padding:14px 28px;border-radius:10px;font-weight:600;font-size:15px;margin:6px 6px 6px 0}
.fr-buy-btn.amazon{background:#ff9900;color:#111!important}
.fr-disclaimer{font-size:12px;color:#999;margin-top:28px;padding-top:16px;border-top:1px solid #eee}
p{font-size:15.5px;color:#333}
</style>"""

def make_affiliate_link(product: dict, lang: str) -> dict:
    original = product.get("link", "")
    if lang == "ko":
        coupang = f"https://link.coupang.com/re/AFFILIATE?lptag={COUPANG_ID}&url={original}"
        return {"coupang": coupang, "amazon": None}
    else:
        sep = "&" if "?" in original else "?"
        amazon = original + f"{sep}tag={AMAZON_ID}" if "amazon.com" in original else original
        return {"coupang": None, "amazon": amazon}

def generate_post(product: dict, lang: str = "ko") -> dict:
    style   = random.choice(KO_STYLES if lang == "ko" else EN_STYLES)
    links   = make_affiliate_link(product, lang)
    reviews = product.get("reviews", {})
    pros_raw = "\n".join(f"- {r}" for r in reviews.get("pros", []))
    cons_raw = "\n".join(f"- {r}" for r in reviews.get("cons", []))

    if lang == "ko":
        buy_btn = f'<a href="{links["coupang"]}" class="fr-buy-btn" target="_blank" rel="nofollow sponsored">쿠팡에서 최저가 확인 →</a>'
        prompt = f"""당신은 실제 제품을 써본 일반인 블로거입니다.

제품: {product['title']} / 가격: {product['price']} / 평점: {product['rating']} / 카테고리: {product['category']}

실제 구매자 리뷰:
좋은점: {pros_raw or '- 사용하기 편리함\n- 가성비 좋음\n- 품질 만족'}
아쉬운점: {cons_raw or '- 배송 포장 다소 부실\n- 설명서 불친절'}

스타일: {style}

아래 HTML 구조로 글을 작성하세요:
<div class="fr-review">
<div class="fr-summary-box"><p class="fr-verdict">한줄 요약</p><p class="fr-one-line">핵심 한 문장</p></div>
<div class="fr-rating"><span class="fr-stars">⭐⭐⭐⭐⭐</span><span class="fr-rating-text">{product['rating']}</span></div>
<p>도입부 2~3문장</p>
<div class="fr-pros-cons">
<div class="fr-pros"><h3>✅ 좋은 점</h3><ul><li>장점1</li><li>장점2</li><li>장점3</li></ul></div>
<div class="fr-cons"><h3>❌ 아쉬운 점</h3><ul><li>단점1</li><li>단점2</li></ul></div>
</div>
<div class="fr-section"><h2>실제로 써보니까</h2><p>상세 리뷰 3~4문단</p></div>
<div class="fr-who"><strong>이런 분께 추천해요</strong>추천 대상 2~3가지<strong style="margin-top:12px">이런 분께는 비추천이에요</strong>비추천 1~2가지</div>
<div class="fr-section">{buy_btn}</div>
<p class="fr-disclaimer">※ 이 글에는 제휴 링크가 포함되어 있습니다.</p>
</div>

JSON으로만 응답: {{"title": "제목(60자이내)", "content": "완성HTML", "excerpt": "요약(150자이내)", "tags": ["태그1","태그2","태그3","태그4","태그5"]}}"""

    else:
        buy_btn = f'<a href="{links["amazon"]}" class="fr-buy-btn amazon" target="_blank" rel="nofollow sponsored">Check Best Price on Amazon →</a>'
        prompt = f"""You are a regular person sharing an honest product review.

Product: {product['title']} / Price: {product['price']} / Rating: {product['rating']} / Category: {product['category']}

Real buyer reviews:
Pros: {pros_raw or '- Easy to use\n- Great value\n- Solid quality'}
Cons: {cons_raw or '- Packaging could be better\n- Manual unclear'}

Style: {style}

Write using this HTML structure:
<div class="fr-review">
<div class="fr-summary-box"><p class="fr-verdict">Bottom line</p><p class="fr-one-line">One sentence summary</p></div>
<div class="fr-rating"><span class="fr-stars">⭐⭐⭐⭐⭐</span><span class="fr-rating-text">{product['rating']}</span></div>
<p>Intro 2-3 sentences</p>
<div class="fr-pros-cons">
<div class="fr-pros"><h3>✅ What I loved</h3><ul><li>pro1</li><li>pro2</li><li>pro3</li></ul></div>
<div class="fr-cons"><h3>❌ What could be better</h3><ul><li>con1</li><li>con2</li></ul></div>
</div>
<div class="fr-section"><h2>My honest take</h2><p>3-4 paragraphs</p></div>
<div class="fr-who"><strong>Who should buy this</strong>2-3 points<strong style="margin-top:12px">Who should skip it</strong>1-2 points</div>
<div class="fr-section">{buy_btn}</div>
<p class="fr-disclaimer">This post contains affiliate links.</p>
</div>

Respond ONLY in JSON: {{"title": "title under 70 chars", "content": "complete HTML", "excerpt": "summary under 160 chars", "tags": ["tag1","tag2","tag3","tag4","tag5"]}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json, re
    raw   = message.content[0].text.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    data  = json.loads(match.group() if match else raw)
    data["content"] = CSS + data["content"]
    data["product"] = product
    data["lang"]    = lang
    return data
