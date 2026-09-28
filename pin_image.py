"""핀터레스트용 세로 이미지(1000x1500) 생성 → 워드프레스 대표 이미지로 업로드.
워드프레스 RSS에 대표 이미지가 실리고, 핀터레스트가 RSS를 읽어 자동으로 핀을 만든다."""
import io
import os
import re
import textwrap

import requests
from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 1500
BG = (250, 246, 240)
INK = (34, 30, 28)
ACCENT = (232, 120, 40)
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

TAGLINES = {
    "en": ("{rating}★ from {count} buyers", "Honest pros & cons →"),
    "es": ("{rating}★ de {count} compradores", "Pros y contras →"),
    "in": ("{rating}★ de {count} compradores", "Prós e contras →"),
    "kr": ("구매자 {count}명 평점 {rating}★", "장단점 정리 →"),
}


def _font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def make_pin(title: str, image_url: str, rating: str, review_count: str, site: str, lang: str = "en") -> bytes:
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    # 상품 사진 (흰 카드 위)
    d.rounded_rectangle((70, 70, W - 70, 870), radius=36, fill=(255, 255, 255))
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        img.thumbnail((W - 220, 720))
        canvas.paste(img, ((W - img.width) // 2, 110 + (720 - img.height) // 2))
    except Exception as e:
        print(f"  핀 이미지: 상품 사진 실패 {e}")

    # 제목
    y = 930
    font = _font(True, 60)
    for line in textwrap.wrap(re.sub(r"\s+", " ", title), width=26)[:4]:
        d.text((80, y), line, font=font, fill=INK)
        y += 74

    # 평점 줄
    rt = (rating or "").split(" ")[0]
    cnt = (review_count or "").strip()
    line1, line2 = TAGLINES.get(lang, TAGLINES["en"])
    if rt and cnt:
        d.text((80, y + 20), line1.format(rating=rt, count=cnt), font=_font(False, 40), fill=(90, 84, 78))
    # 하단 띠
    d.rectangle((0, H - 150, W, H), fill=ACCENT)
    d.text((80, H - 112), line2, font=_font(True, 46), fill=(255, 255, 255))
    d.text((W - 80, H - 185), site, font=_font(False, 32), fill=(140, 132, 124), anchor="ra")

    buf = io.BytesIO()
    canvas.save(buf, "JPEG", quality=88)
    return buf.getvalue()


def upload_featured(wp_url: str, auth_header: dict, post_data: dict, lang: str) -> int:
    """핀 이미지를 만들어 미디어로 올리고 media id 반환 (실패 시 0)."""
    p = post_data.get("product", {})
    if not p.get("image"):
        return 0
    try:
        site = re.sub(r"^https?://", "", wp_url).rstrip("/")
        data = make_pin(post_data["title"], p["image"], p.get("rating", ""), p.get("review_count", ""), site, lang)
        slug = re.sub(r"[^a-z0-9]+", "-", post_data["title"].lower()).strip("-")[:50] or "pin"
        r = requests.post(
            wp_url + "/wp-json/wp/v2/media",
            headers={**auth_header, "Content-Disposition": f'attachment; filename="{slug}-pin.jpg"',
                     "Content-Type": "image/jpeg"},
            data=data, timeout=90)
        if r.status_code == 201:
            mid = r.json()["id"]
            requests.post(wp_url + f"/wp-json/wp/v2/media/{mid}", headers=auth_header,
                          json={"alt_text": post_data["title"]}, timeout=30)
            return mid
        print(f"  핀 이미지 업로드 실패: {r.status_code} {r.text[:150]}")
    except Exception as e:
        print(f"  핀 이미지 오류: {e}")
    return 0
