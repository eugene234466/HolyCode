from apscheduler.schedulers.background import BackgroundScheduler
from services.bible import get_verse_of_day
from services.groq_ai import generate_devotional, generate_challenge
from database.db import get_conn


def generate_daily_devotional():
    try:
        verse = get_verse_of_day()
        if not verse:
            print("Error: Could not fetch verse of the day")
            return

        result = generate_devotional(verse['text'], verse['reference'])

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO daily_devotional (verse_reference, verse_text, language, code_snippet)
            VALUES (%s, %s, %s, %s)
        """, (result['reference'], verse['text'], result['language'], result['code']))
        conn.commit()
        cur.close()
        conn.close()

        print("✅ Daily devotional generated!")

    except Exception as e:
        print(f"❌ Devotional generation error: {e}")


def generate_daily_challenge():
    try:
        result = generate_challenge()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO daily_challenge (verse_reference, verse_text, prompt)
            VALUES (%s, %s, %s)
        """, (result['reference'], result['verse_text'], result['prompt']))
        conn.commit()
        cur.close()
        conn.close()

        print("✅ Daily challenge generated!")

    except Exception as e:
        print(f"❌ Challenge generation error: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        generate_daily_devotional,
        trigger='cron',
        hour=0,
        minute=0,
        id='daily_devotional'
    )

    scheduler.add_job(
        generate_daily_challenge,
        trigger='cron',
        hour=0,
        minute=1,
        id='daily_challenge'
    )

    scheduler.start()
    print("✅ Scheduler started!")
    return scheduler