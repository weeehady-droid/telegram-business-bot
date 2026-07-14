from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = 5260085571

replies = {
    "usdt": """<blockquote>Enter and click on any wallet to be copied <tg-emoji emoji-id="5332668748044204575"></tg-emoji></blockquote>

<blockquote>- Binance <tg-emoji emoji-id="5420232672964275159"></tg-emoji> : (1156755586)</blockquote>

<blockquote>- Bybit <tg-emoji emoji-id="5433900293987261516"></tg-emoji> : (523496990)</blockquote>

<blockquote><tg-emoji emoji-id="5832251986635920010"></tg-emoji> Don't forget to take a screenshot
of the transaction you made.</blockquote>"""
}


def send(chat_id, text, business_connection_id=None):
    payload = {
        "chat_id": chat_id,
        "text": "X Enter and click on any wallet to be copied\n\n- Binance : (1156755586)\n\n- Bybit : (523496990)\n\nX Don't forget to take a screenshot of the transaction you made.",
        "entities": [
            {
                "offset": 0,
                "length": 1,
                "type": "custom_emoji",
                "custom_emoji_id": "5332668748044204575"
            },
            {
                "offset": 80,
                "length": 1,
                "type": "custom_emoji",
                "custom_emoji_id": "5832251986635920010"
            }
        ]
    }

    if business_connection_id:
        payload["business_connection_id"] = business_connection_id

    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json=payload
    )

    print(r.status_code)
    print(r.text)


@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(data)

    if "business_message" in data:

        msg = data["business_message"]

        # يرد على رسائلك أنت فقط
        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        text = msg.get("text", "").strip().lower()
        chat_id = msg["chat"]["id"]
        business_connection_id = msg["business_connection_id"]

        if text in replies:
            send(chat_id, replies[text], business_connection_id)

    elif "message" in data:

        msg = data["message"]

        # يرد على رسائلك أنت فقط
        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        text = msg.get("text", "").strip().lower()
        chat_id = msg["chat"]["id"]

        if text in replies:
            send(chat_id, replies[text])

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
