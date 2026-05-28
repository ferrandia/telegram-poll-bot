#!/usr/bin/env python3
"""Publica una encuesta en un grupo de Telegram a partir de config.json."""
import json
import os
import sys
import urllib.error
import urllib.request

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def send_poll(token, chat_id, config):
    url = f"https://api.telegram.org/bot{token}/sendPoll"
    payload = {
        "chat_id": chat_id,
        "question": config["question"],
        "options": [{"text": opt} for opt in config["options"]],
        "is_anonymous": config.get("is_anonymous", True),
        "allows_multiple_answers": config.get("allows_multiple_answers", False),
        "type": config.get("poll_type", "regular"),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        sys.exit("ERROR: faltan las variables de entorno BOT_TOKEN y/o CHAT_ID")

    config = load_config()
    try:
        result = send_poll(token, chat_id, config)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        sys.exit(f"ERROR de Telegram ({e.code}): {body}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR de red: {e.reason}")

    if result.get("ok"):
        print("Encuesta publicada correctamente.")
    else:
        sys.exit(f"Telegram devolvió un error: {result}")


if __name__ == "__main__":
    main()
