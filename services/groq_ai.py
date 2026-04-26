from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)
model = "llama-3.3-70b-versatile"


def generate_devotional(verse_text, verse_reference):
    prompt = f"""You are HolyCode. Write a short code snippet that creatively represents this scripture as actual code.
Pick any programming language you like.
Return ONLY in this exact format with no extra text:
REFERENCE: <book chapter:verse>
LANGUAGE: <language name>
CODE:
<code snippet only, no markdown backticks>

VERSE: {verse_reference} - {verse_text}"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
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

    code = "\n".join(code_lines).strip()
    # Strip any markdown backticks Groq might sneak in
    code = code.replace("```python", "").replace("```javascript", "").replace("```php", "").replace("```java", "").replace("```", "").strip()

    return {
        "reference": reference,
        "language": language,
        "code": code
    }


def generate_challenge():
    prompt = """You are HolyCode. Pick a random Bible verse that would make an interesting programming challenge.
Then write a short, fun and inspiring challenge prompt telling developers to interpret it as code or pseudocode.
Return ONLY in this exact format with no extra text:
REFERENCE: <book chapter:verse>
TEXT: <verse text>
PROMPT: <challenge prompt>"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
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
