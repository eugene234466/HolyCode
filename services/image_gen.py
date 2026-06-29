import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import quote

# /tmp is writable on Vercel but ephemeral — fine for single request lifetime
CARDS_DIR = "/tmp/images/cards"
AI_DIR = "/tmp/images/ai"


def init_dirs():
    os.makedirs(CARDS_DIR, exist_ok=True)
    os.makedirs(AI_DIR, exist_ok=True)


def generate_code_card(code, language, reference):
    init_dirs()

    width, height = 800, 500
    bg_color = (13, 15, 20)
    gold = (201, 168, 76)
    white = (232, 230, 224)
    muted = (107, 104, 120)
    bar_color = (21, 21, 32)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_path = os.path.join(os.path.dirname(__file__), "../static/fonts/JetBrainsMono-Regular.ttf")
        font_code = ImageFont.truetype(font_path, 16)
        font_label = ImageFont.truetype(font_path, 14)
        font_title = ImageFont.truetype(font_path, 18)
    except:
        font_code = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_title = ImageFont.load_default()

    # Top bar
    draw.rectangle([0, 0, width, 50], fill=bar_color)
    draw.rectangle([0, 0, width, 3], fill=gold)

    # Traffic lights
    draw.ellipse([16, 18, 28, 30], fill=(255, 95, 87))
    draw.ellipse([36, 18, 48, 30], fill=(254, 188, 46))
    draw.ellipse([56, 18, 68, 30], fill=(40, 200, 64))

    draw.text((90, 16), f"// {language}", font=font_title, fill=gold)

    ref_bbox = draw.textbbox((0, 0), reference, font=font_label)
    ref_width = ref_bbox[2] - ref_bbox[0]
    draw.text((width - ref_width - 20, 18), reference, font=font_label, fill=muted)

    draw.rectangle([0, height - 3, width, height], fill=gold)
    draw.text((20, height - 26), "✦ HolyCode", font=font_label, fill=gold)

    # Code lines
    x, y = 20, 68
    line_height = 22
    max_lines = int((height - 100) / line_height)

    for i, line in enumerate(code.splitlines()[:max_lines]):
        draw.text((x, y), f"{i+1:2}", font=font_code, fill=muted)
        draw.text((x + 40, y), line, font=font_code, fill=white)
        y += line_height

    # Return image as bytes instead of saving to disk
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def generate_ai_image(verse_text, reference):
    prompt = (
        f"A dramatic cinematic digital painting inspired by the Bible verse {reference}: '{verse_text}'. "
        f"Ancient biblical setting, sweeping landscape, divine golden light rays breaking through clouds, "
        f"deep symbolic imagery, rich warm colors, oil painting style, highly detailed brushwork, "
        f"epic grand composition, spiritual atmosphere, sacred mood, "
        f"no text, no letters, no words, no captions"
    )
    encoded_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&nologo=true&seed=42"

    try:
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            return None

        # Return image as bytes instead of saving to disk
        buffer = BytesIO(response.content)
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"AI image generation error: {e}")
        return None
