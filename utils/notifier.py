import json
import urllib.request
import urllib.error
import time

def send_discord_message(webhook_url, message=None, embed=None):
    """
    Sends a message to a Discord Webhook.
    :param webhook_url: The discord webhook URL.
    :param message: The content string.
    :param embed: A dictionary representing the embed object.
    """
    if not webhook_url:
        return

    payload = {}
    if message:
        payload["content"] = message
    if embed:
        payload["embeds"] = [embed]

    if not payload:
        return

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CoCBot/1.0"
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            if response.status not in (200, 204):
                print(f"⚠️ Discord webhook returned status {response.status}")
    except urllib.error.URLError as e:
        print(f"⚠️ Failed to send Discord notification: {e}")

def send_attack_summary(webhook_url, attack_number, gold, elixir, dark_elixir, trophies=None, duration=None):
    """
    Helper to send an attack summary embed.
    """
    if not webhook_url:
        return

    embed = {
        "title": f"⚔️ Attack #{attack_number} Summary",
        "color": 65280,  # Green
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "fields": [
            {"name": "💰 Gold", "value": f"{gold:,}", "inline": True},
            {"name": "🧪 Elixir", "value": f"{elixir:,}", "inline": True},
            {"name": "⚫ Dark Elixir", "value": f"{dark_elixir:,}", "inline": True}
        ],
        "footer": {
            "text": "CoC Bot Notification"
        }
    }
    
    if trophies:
        embed["fields"].append({"name": "🏆 Trophies", "value": str(trophies), "inline": True})
    
    if duration:
        embed["fields"].append({"name": "⏱ Duration", "value": f"{duration:.1f}s", "inline": True})

    send_discord_message(webhook_url, embed=embed)

def send_session_start(webhook_url):
    if not webhook_url:
        return
    
    embed = {
        "title": "🚀 Bot Session Started",
        "color": 3447003,  # Blue
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "description": "The Clash of Clans bot has started running."
    }
    send_discord_message(webhook_url, embed=embed)
