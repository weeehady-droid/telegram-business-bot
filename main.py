from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = 5260085571

replies = {
    "usdt": """<blockquote><b>💳 Payment Details</b></blockquote>

<blockquote>🟨 <b>Binance UID</b>
<code>1156755586</code></blockquote>

<blockquote>⚫ <b>Bybit UID</b>
<code>523496990</code></blockquote>

<blockquote>📸 Please send a screenshot after completing the payment.</blockquote>"""
}


def send(chat_id, text, business_connection_id=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "🟨 Open Binance",
                        "url": "https://www.binance.com/"
                    }
                ],
                [
                    {
                        "text": "⚫ Open Bybit",
                        "url": "https://www.bybit.com/"
                    }
                ]
            ]
        }
    }

    if business_connection_id:
        payload["business_connection_id"] = business_connection_id

    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json=payload
    )

    print("Status:", r.status_code)
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

        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        text = msg.get("text", "").strip().lower()

        if text in replies:
            send(
                msg["chat"]["id"],
                replies[text],
                msg["business_connection_id"]
            )

    elif "message" in data:
        msg = data["message"]

        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        text = msg.get("text", "").strip().lower()

        if text in replies:
            send(msg["chat"]["id"], replies[text])

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
