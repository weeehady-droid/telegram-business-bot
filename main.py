from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = 5260085571


def send(chat_id, business_connection_id=None):
    text = "⭐ Enter and click on any wallet to be copied\n\n⭐ Binance : (1156755586)\n\n⭐ Bybit : (523496990)\n\n⭐ Don't forget to take a screenshot of the transaction you made."

    payload = {
        "chat_id": chat_id,
        "text": text,
        "entities": [
            {
                "offset": 0,
                "length": 1,
                "type": "custom_emoji",
                "custom_emoji_id": "5332668748044204575"
            },
            {
                "offset": 46,
                "length": 1,
                "type": "custom_emoji",
                "custom_emoji_id": "5420232672964275159"
            },
            {
                "offset": 71,
                "length": 1,
                "type": "custom_emoji",
                "custom_emoji_id": "5433900293987261516"
            },
            {
                "offset": 99,
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

    print("========== SEND MESSAGE ==========")
    print("Status Code:", r.status_code)
    print("Response:", r.text)
    print("==================================")


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

        if text == "usdt":
            send(
                msg["chat"]["id"],
                msg["business_connection_id"]
            )

    elif "message" in data:
        msg = data["message"]

        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        text = msg.get("text", "").strip().lower()

        if text == "usdt":
            send(msg["chat"]["id"])

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
