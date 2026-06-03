import re
from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)
model = "llama-3.3-70b-versatile"


def clean_code(text):
    """Strip markdown backticks and language tags from code"""
    text = re.sub(r'```[\w]*\n?', '', text)
    text = text.replace('```', '')
    return text.strip()


def generate_devotional(verse_text, verse_reference):
    prompt = f"""You are HolyCode. Write a short, creative code snippet that represents this Bible verse as actual working code.
Pick any programming language you like. Be creative and make it meaningful.
Return ONLY in this exact format with no extra text and absolutely no markdown backticks:

REFERENCE: <book chapter:verse>
LANGUAGE: <language name>
CODE:
<code snippet only, no markdown, no backticks>

VERSE: {verse_reference} - {verse_text}"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    text = response.choices[0].message.content.strip()
    lines = text.splitlines()

    reference = ""
    language = ""
    code_lines = []
    code_started = False

    for line in lines:
        if line.startswith("REFERENCE:"):
            reference = line.replace("REFERENCE:", "").strip()
        elif line.startswith("LANGUAGE:"):
            language = line.replace("LANGUAGE:", "").strip()
        elif line.startswith("CODE:"):
            code_started = True
        elif code_started:
            code_lines.append(line)

    code = clean_code("\n".join(code_lines))

    return {
        "reference": reference,
        "language": language,
        "code": code
    }


def generate_challenge(used_verses=None):
    """Generate a daily challenge with a verse not previously used"""
    if used_verses is None:
        used_verses = []

    exclude_text = ""
    if used_verses:
        exclude_list = ", ".join(used_verses[:20])
        exclude_text = f"\n\nIMPORTANT: Do NOT use any of these verses that have already been used: {exclude_list}\nPick a completely different verse from a different book of the Bible."

    prompt = f"""You are HolyCode. Pick a unique and interesting Bible verse that would make a great programming challenge.
Choose from a wide variety of books — Old Testament, New Testament, Psalms, Proverbs, Gospels, Epistles.
Write a short, fun and inspiring challenge prompt telling developers to interpret the verse as code or pseudocode.
Be creative with the challenge — suggest metaphors, algorithms, or programming concepts that could represent the verse.{exclude_text}

Return ONLY in this exact format with no extra text:
REFERENCE: <book chapter:verse>
TEXT: <verse text>
PROMPT: <challenge prompt, 2-3 sentences max>"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )

    text = response.choices[0].message.content.strip()
    lines = text.splitlines()

    reference = ""
    verse_text = ""
    prompt_lines = []
    prompt_started = False

    for line in lines:
        if line.startswith("REFERENCE:"):
            reference = line.replace("REFERENCE:", "").strip()
        elif line.startswith("TEXT:"):
            verse_text = line.replace("TEXT:", "").strip()
        elif line.startswith("PROMPT:"):
            prompt_started = True
            prompt_lines.append(line.replace("PROMPT:", "").strip())
        elif prompt_started:
            prompt_lines.append(line)

    return {
        "reference": reference,
        "verse_text": verse_text,
        "prompt": "\n".join(prompt_lines).strip()
    }


def explain_concept(code, format):
    prompt = f"""You are a friendly programming teacher on HolyCode.
Look at this {format} and identify the main programming concept used.
Explain it in simple plain English for a complete beginner.
Give one short beginner-friendly example.
Keep your response under 150 words.

{format.upper()}:
{code}"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()


def pick_challenge_verse():
    from services.bible import get_verse_of_day
    return get_verse_of_day()
