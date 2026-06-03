from services.bible import get_verse_of_day
from services.groq_ai import generate_devotional, generate_challenge
from services.notifications import notify_new_devotional, notify_new_challenge
from database.db import get_conn, get_used_verses, mark_verse_used


def generate_daily_devotional():
    """Generate and save today's devotional"""
    try:
        verse = get_verse_of_day()
        if not verse:
            print("❌ Could not fetch verse of the day")
            return False

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

        # Send push notifications
        notify_new_devotional()

        return True

    except Exception as e:
        print(f"❌ Devotional generation error: {e}")
        return False


def generate_daily_challenge():
    """Generate and save today's challenge, avoiding repeats"""
    try:
        # Get previously used verses
        used_verses = get_used_verses()

        result = generate_challenge(used_verses=used_verses)

        if not result['reference']:
            print("❌ Could not generate challenge")
            return False

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO daily_challenge (verse_reference, verse_text, prompt)
            VALUES (%s, %s, %s)
        """, (result['reference'], result['verse_text'], result['prompt']))
        conn.commit()
        cur.close()
        conn.close()

        # Mark verse as used
        mark_verse_used(result['reference'])

        print(f"✅ Daily challenge generated! ({result['reference']})")

        # Send push notifications
        notify_new_challenge()

        return True

    except Exception as e:
        print(f"❌ Challenge generation error: {e}")
        return False


def start_scheduler():
    """Start APScheduler for Render deployment"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

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

    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        return None
