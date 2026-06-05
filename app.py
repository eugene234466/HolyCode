import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from services.groq_ai import explain_concept
from services.image_gen import generate_code_card, generate_ai_image
from services.notifications import notify_winner
from database.db import get_conn, init_db, delete_subscription

app = Flask(__name__)

# ─── STARTUP ───
with app.app_context():
    init_db()

    # Only use APScheduler on Render (not Vercel serverless)
    if os.environ.get("VERCEL") != "1":
        from services.scheduler import start_scheduler, generate_daily_devotional, generate_daily_challenge

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT id FROM daily_devotional WHERE DATE(created_at) = CURRENT_DATE")
        if not cur.fetchone():
            generate_daily_devotional()

        cur.execute("SELECT id FROM daily_challenge WHERE DATE(created_at) = CURRENT_DATE")
        if not cur.fetchone():
            generate_daily_challenge()

        cur.close()
        conn.close()
        start_scheduler()
    else:
        print("✅ Running on Vercel — using cron endpoints instead of APScheduler")


# ─── VERCEL CRON ENDPOINTS ───

def verify_cron_secret():
    """Verify request comes from Vercel cron"""
    secret = request.headers.get("Authorization", "").replace("Bearer ", "")
    return secret == os.environ.get("CRON_SECRET", "")


@app.route("/cron/devotional")
def cron_devotional():
    if not verify_cron_secret():
        return jsonify({"error": "Unauthorized"}), 401

    from services.scheduler import generate_daily_devotional
    success = generate_daily_devotional()
    return jsonify({"success": success})


@app.route("/cron/challenge")
def cron_challenge():
    if not verify_cron_secret():
        return jsonify({"error": "Unauthorized"}), 401

    from services.scheduler import generate_daily_challenge
    success = generate_daily_challenge()
    return jsonify({"success": success})


# ─── MAIN ROUTES ───

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM daily_devotional
        WHERE DATE(created_at) = CURRENT_DATE
        ORDER BY created_at DESC LIMIT 1
    """)
    devotional = cur.fetchone()

    cur.execute("""
        SELECT * FROM daily_challenge
        WHERE DATE(created_at) = CURRENT_DATE
        ORDER BY created_at DESC LIMIT 1
    """)
    challenge = cur.fetchone()

    submissions = []
    if challenge:
        cur.execute("""
            SELECT s.* FROM submissions s
            JOIN daily_challenge c ON s.challenge_id = c.id
            WHERE DATE(c.created_at) = CURRENT_DATE
            ORDER BY s.likes DESC, s.created_at DESC
        """)
        submissions = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html",
                           devotional=devotional,
                           challenge=challenge,
                           submissions=submissions,
                           now=datetime.now())


@app.route("/archive")
def archive():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM daily_devotional ORDER BY created_at DESC")
    devotionals = cur.fetchall()

    cur.execute("SELECT * FROM daily_challenge ORDER BY created_at DESC")
    challenges = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("archive.html",
                           devotionals=devotionals,
                           challenges=challenges)


@app.route("/submission/<int:id>")
def submission(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM submissions WHERE id = %s", (id,))
    sub = cur.fetchone()

    if not sub:
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.execute("SELECT * FROM daily_challenge WHERE id = %s", (sub[1],))
    challenge = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("submission.html", submission=sub, challenge=challenge)


@app.route("/submit", methods=["POST"])
def submit():
    username = request.form.get("username", "Anonymous").strip() or "Anonymous"
    fmt = request.form.get("format", "code").strip()
    language = request.form.get("language", "").strip()
    code = request.form.get("code", "").strip()

    if not code:
        return redirect(url_for("index"))

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM daily_challenge
        WHERE DATE(created_at) = CURRENT_DATE
        ORDER BY created_at DESC LIMIT 1
    """)
    challenge = cur.fetchone()

    if not challenge:
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.execute("""
        INSERT INTO submissions (challenge_id, username, format, language, code)
        VALUES (%s, %s, %s, %s, %s)
    """, (challenge[0], username, fmt, language, code))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("index"))


@app.route("/like/<int:submission_id>", methods=["POST"])
def like(submission_id):
    ip = request.remote_addr

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM likes
        WHERE submission_id = %s AND ip_address = %s
    """, (submission_id, ip))

    existing = cur.fetchone()

    if existing:
        cur.execute("DELETE FROM likes WHERE submission_id = %s AND ip_address = %s", (submission_id, ip))
        cur.execute("UPDATE submissions SET likes = GREATEST(likes - 1, 0) WHERE id = %s", (submission_id,))
        action = "unliked"
    else:
        cur.execute("INSERT INTO likes (submission_id, ip_address) VALUES (%s, %s)", (submission_id, ip))
        cur.execute("UPDATE submissions SET likes = likes + 1 WHERE id = %s", (submission_id,))
        action = "liked"

    conn.commit()

    cur.execute("SELECT likes FROM submissions WHERE id = %s", (submission_id,))
    updated = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify({"success": True, "likes": updated[0], "action": action})


@app.route("/explain", methods=["POST"])
def explain():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    code = data.get("code", "").strip()
    fmt = data.get("format", "code")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    explanation = explain_concept(code, fmt)
    return jsonify({"explanation": explanation})


@app.route("/card/<int:submission_id>")
def card(submission_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM submissions WHERE id = %s", (submission_id,))
    sub = cur.fetchone()

    if not sub:
        cur.close()
        conn.close()
        return jsonify({"error": "Submission not found"}), 404

    cur.execute("SELECT * FROM daily_challenge WHERE id = %s", (sub[1],))
    challenge = cur.fetchone()

    cur.close()
    conn.close()

    language = sub[4] if sub[4] else sub[3]
    reference = challenge[1] if challenge else "HolyCode"
    code = sub[5]

    filename = generate_code_card(code, language, reference)
    filepath = os.path.join("static", "images", "cards", filename)

    return send_file(filepath, mimetype="image/png")


@app.route("/ai-image/<int:submission_id>")
def ai_image(submission_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM submissions WHERE id = %s", (submission_id,))
    sub = cur.fetchone()

    if not sub:
        cur.close()
        conn.close()
        return jsonify({"error": "Submission not found"}), 404

    cur.execute("SELECT * FROM daily_challenge WHERE id = %s", (sub[1],))
    challenge = cur.fetchone()

    cur.close()
    conn.close()

    verse_text = challenge[2] if challenge else ""
    reference = challenge[1] if challenge else "HolyCode"

    filename = generate_ai_image(verse_text, reference)
    if not filename:
        return jsonify({"error": "Image generation failed"}), 500

    filepath = os.path.join("/tmp", "images", "ai", filename)
    return send_file(filepath, mimetype="image/png")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    subscription_info = data.get("subscription")

    if not subscription_info:
        return jsonify({"error": "No subscription info"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO push_subscriptions (subscription_info)
        VALUES (%s)
        RETURNING id
    """, (json.dumps(subscription_info),))

    sub_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "id": sub_id})


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.get_json()
    sub_id = data.get("id")

    if not sub_id:
        return jsonify({"error": "No subscription ID"}), 400

    delete_subscription(sub_id)
    return jsonify({"success": True})


@app.route("/notify/winner/<int:submission_id>", methods=["POST"])
def notify_winner_route(submission_id):
    """Manually trigger winner notification — admin only"""
    secret = request.headers.get("Authorization", "").replace("Bearer ", "")
    if secret != os.environ.get("CRON_SECRET", ""):
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT username FROM submissions WHERE id = %s", (submission_id,))
    sub = cur.fetchone()

    cur.execute("""
        SELECT c.verse_reference FROM daily_challenge c
        JOIN submissions s ON s.challenge_id = c.id
        WHERE s.id = %s
    """, (submission_id,))
    challenge = cur.fetchone()
    cur.close()
    conn.close()

    if not sub:
        return jsonify({"error": "Submission not found"}), 404

    result = notify_winner(sub[0], challenge[0] if challenge else "today's verse")
    return jsonify(result)


@app.route("/favicon.ico")
def favicon():
    return send_file("static/images/icon-192.png", mimetype="image/png")


@app.route("/manifest.json")
def manifest():
    return send_file("static/manifest.json")


@app.route("/sw.js")
def service_worker():
    return send_file("sw.js", mimetype="application/javascript")


if __name__ == "__main__":
    app.run(debug=True)
