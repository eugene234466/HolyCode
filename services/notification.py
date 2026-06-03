import json
from pywebpush import webpush, WebPushException
from config import Config
from database.db import get_all_subscriptions, delete_subscription


def send_push_notification(subscription_info, title, body, url="/"):
    """Send a push notification to a single subscriber"""
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({
                "title": title,
                "body": body,
                "url": url
            }),
            vapid_private_key=Config.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": f"mailto:{Config.VAPID_EMAIL}"
            }
        )
        return True
    except WebPushException as e:
        # 410 Gone = subscription expired/unsubscribed
        if e.response and e.response.status_code == 410:
            return "expired"
        print(f"Push error: {e}")
        return False
    except Exception as e:
        print(f"Push error: {e}")
        return False


def notify_all(title, body, url="/"):
    """Send push notification to all subscribers, clean up expired ones"""
    subscriptions = get_all_subscriptions()
    sent = 0
    failed = 0
    cleaned = 0

    for sub_id, sub_info in subscriptions:
        if isinstance(sub_info, str):
            sub_info = json.loads(sub_info)

        result = send_push_notification(sub_info, title, body, url)

        if result is True:
            sent += 1
        elif result == "expired":
            delete_subscription(sub_id)
            cleaned += 1
        else:
            failed += 1

    print(f"✅ Notifications: {sent} sent, {failed} failed, {cleaned} expired cleaned")
    return {"sent": sent, "failed": failed, "cleaned": cleaned}


def notify_new_devotional():
    return notify_all(
        title="✦ HolyCode — Daily Devotional",
        body="Today's scripture is written as code. Come read it! 🙏",
        url="/"
    )


def notify_new_challenge():
    return notify_all(
        title="⚡ HolyCode — Daily Challenge",
        body="A new scripture challenge is live. Can you code it? 💻",
        url="/#challenge"
    )


def notify_winner(username, verse_ref):
    return notify_all(
        title="🏆 HolyCode — Today's Winner",
        body=f"{username}'s interpretation of {verse_ref} won today's challenge!",
        url="/"
    )
