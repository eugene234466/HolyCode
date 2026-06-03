import psycopg2
from config import Config


def get_conn():
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_devotional (
            id SERIAL PRIMARY KEY,
            verse_reference TEXT,
            verse_text TEXT,
            language TEXT,
            code_snippet TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS daily_challenge (
            id SERIAL PRIMARY KEY,
            verse_reference TEXT,
            verse_text TEXT,
            prompt TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            challenge_id INTEGER REFERENCES daily_challenge(id),
            username TEXT DEFAULT 'Anonymous',
            format TEXT,
            language TEXT,
            code TEXT,
            likes INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS likes (
            id SERIAL PRIMARY KEY,
            submission_id INTEGER REFERENCES submissions(id),
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id SERIAL PRIMARY KEY,
            subscription_info JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS used_verses (
            id SERIAL PRIMARY KEY,
            verse_reference TEXT UNIQUE,
            used_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_used_verses():
    """Return list of verse references already used as challenges"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT verse_reference FROM used_verses ORDER BY used_at DESC LIMIT 50")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]


def mark_verse_used(verse_reference):
    """Mark a verse reference as used"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO used_verses (verse_reference)
        VALUES (%s)
        ON CONFLICT (verse_reference) DO UPDATE SET used_at = NOW()
    """, (verse_reference,))
    conn.commit()
    cur.close()
    conn.close()


def get_all_subscriptions():
    """Return all push subscriptions"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, subscription_info FROM push_subscriptions")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def delete_subscription(subscription_id):
    """Delete a push subscription"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM push_subscriptions WHERE id = %s", (subscription_id,))
    conn.commit()
    cur.close()
    conn.close()
