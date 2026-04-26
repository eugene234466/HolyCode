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
    """)
    conn.commit()
    cur.close()
    conn.close()