import requests
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import quote

CARDS_DIR = os.path.join("static", "images", "cards")
AI_DIR = os.path.join("static", "images", "ai")

os.makedirs(CARDS_DIR, exist_ok=True)
os.makedirs(AI_DIR, exist_ok=True)

def generate_code_card(code, language, reference):
    # Canvas
    width, height = 800, 500
    bg_color = (13, 15, 20)        # #0d0f14
    gold = (240, 165, 0)           # #f0a500
    white = (238, 240, 246)        # #eef0f6
    muted = (136, 144, 168)        # #8890a8
    bar_color = (26, 30, 42)       # #1a1e2a

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load monospace font, fallback to default
    try:
        font_code = ImageFont.truetype("static/fonts/JetBrainsMono-Regular.ttf", 16)
        font_label = ImageFont.truetype("static/fonts/JetBrainsMono-Regular.ttf", 14)
        font_title = ImageFont.truetype("static/fonts/JetBrainsMono-Regular.ttf", 18)
    except:
        font_code = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_title = ImageFont.load_default()

    # Top bar
    draw.rectangle([0, 0, width, 50], fill=bar_color)

    # Gold accent line
    draw.rectangle([0, 0, width, 3], fill=gold)

    # Language label
    draw.text((20, 15), f"// {language}", font=font_title, fill=gold)

    # Reference on top right
    ref_bbox = draw.textbbox((0, 0), reference, font=font_label)
    ref_width = ref_bbox[2] - ref_bbox[0]
    draw.text((width - ref_width - 20, 18), reference, font=font_label, fill=muted)

    # HolyCode watermark bottom right
    watermark = "HolyCode"
    wm_bbox = draw.textbbox((0, 0), watermark, font=font_label)
    wm_width = wm_bbox[2] - wm_bbox[0]
    draw.text((width - wm_width - 20, height - 30), watermark, font=font_label, fill=gold)

    # Code lines
    x, y = 20, 70
    line_height = 22
    max_lines = int((height - 100) / line_height)

    for i, line in enumerate(code.splitlines()[:max_lines]):
        # Line numbers
        draw.text((x, y), f"{i+1:2}", font=font_code, fill=muted)
        # Code text
        draw.text((x + 40, y), line, font=font_code, fill=white)
        y += line_height

    # Save
    filename = f"card_{reference.replace(' ', '_').replace(':', '-')}.png"
    filepath = os.path.join(CARDS_DIR, filename)
    img.save(filepath)

    return filename


def generate_ai_image(verse_text, reference):
    prompt = f"Biblical scene representing: {verse_text}. Digital art, cinematic lighting, dramatic, detailed, ultra HD"
    encoded_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&nologo=true"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            filename = f"ai_{reference.replace(' ', '_').replace(':', '-')}.png"
            filepath = os.path.join(AI_DIR, filename)

            img = Image.open(BytesIO(response.content))
            img.save(filepath)

            return filename
        return None
    except Exception as e:
        print(f"AI image generation error: {e}")
        return None