import anthropic
import os
import random

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# 사람 같은 느낌을 주는 글쓰기 스타일 변형
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

def generate_post(product: dict, lang: str = "ko") -> dict:
    style = random.choice(KO_STYLES if lang == "ko" else EN_STYLES)
    
    if lang == "ko":
        prompt = f"""
당신은 실제 제품을 사용해본 일반인 블로거입니다. 아래 제품에 대해 블로그 글을 써주세요.

제품 정보:
- 이름: {product['title']}
- 가격: {product['price']}
- 평점: {product['rating']}
- 카테고리: {product['category']}

글쓰기 스타일: {style}

요구사항:
1. 제목은 검색에 잘 걸리면서도 자연스럽게 (60자 이내)
2. 본문은 700~900자 분량
3. 실제 사용 경험을 가진 것처럼 자연스럽게 작성
4. AI가 쓴 느낌이 나지 않게, 구어체와 개인적 표현 섞기
5. 장점 3가지, 단점 1~2가지 솔직하게 언급
6. 마지막에 구매 추천 멘트 자연스럽게 포함
7. HTML 태그 사용 가능 (<h2>, <p>, <ul>, <li>, <strong>)
8. 구매 링크는 다음 형식으로: <a href="{product['link']}" target="_blank" rel="nofollow">👉 최저가 확인하기</a>

다음 JSON 형식으로만 응답하세요:
{{"title": "제목", "content": "HTML 본문 내용", "excerpt": "요약 (150자)", "tags": ["태그1", "태그2", "태그3"]}}
"""
    else:
        prompt = f"""
You are a regular person who has used this product and is sharing your honest experience on a blog.

Product Info:
- Name: {product['title']}
- Price: {product['price']}
- Rating: {product['rating']}
- Category: {product['category']}

Writing style: {style}

Requirements:
1. Title should be SEO-friendly but natural (under 70 characters)
2. Body should be 600-800 words
3. Write as if you've actually used the product
4. Avoid AI-sounding language, use personal voice and casual expressions
5. Mention 3 pros and 1-2 honest cons
6. Include a natural purchase recommendation at the end
7. Use HTML tags (<h2>, <p>, <ul>, <li>, <strong>)
8. Purchase link format: <a href="{product['link']}" target="_blank" rel="nofollow">👉 Check Best Price</a>

Respond ONLY in this JSON format:
{{"title": "title here", "content": "HTML body content", "excerpt": "summary (under 160 chars)", "tags": ["tag1", "tag2", "tag3"]}}
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json, re
    raw = message.content[0].text.strip()
    # JSON 파싱
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        data = json.loads(match.group())
    else:
        data = json.loads(raw)

    data["product"] = product
    data["lang"] = lang
    return data
