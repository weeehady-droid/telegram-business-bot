from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = 5260085571

BINANCE_UID = "1156755586"
BYBIT_UID = "523496990"

MAIN_MESSAGE = """<blockquote><tg-emoji emoji-id="5332668748044204575"></tg-emoji> <b>Payment Details</b></blockquote>

<blockquote><tg-emoji emoji-id="5420232672964275159"></tg-emoji> <b>Binance UID</b>

<code>1156755586</code></blockquote>

<blockquote><tg-emoji emoji-id="5433900293987261516"></tg-emoji> <b>Bybit UID</b>

<code>523496990</code></blockquote>

<blockquote><tg-emoji emoji-id="5832251986635920010"></tg-emoji> Please send a screenshot after completing the payment.</blockquote>
"""

def telegram(method, payload):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        json=payload
    )
    print(r.text)
    return r


def send_payment(chat_id, business_connection_id=None):

    payload = {
        "chat_id": chat_id,
        "text": MAIN_MESSAGE,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "📋 Binance UID",
                        "callback_data": "binance"
                    }
                ],
                [
                    {
                        "text": "📋 Bybit UID",
                        "callback_data": "bybit"
                    }
                ]
            ]
        }
    }

    if business_connection_id:
        payload["business_connection_id"] = business_connection_id

    telegram("sendMessage", payload)


def send_uid(chat_id, title, uid, business_connection_id=None):

    payload = {
        "chat_id": chat_id,
        "text": f"<b>{title}</b>\n\n<code>{uid}</code>",
        "parse_mode": "HTML"
    }

    if business_connection_id:
        payload["business_connection_id"] = business_connection_id

    telegram("sendMessage", payload)


@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    print(data)

    # Telegram Business Messages
    if "business_message" in data:

        msg = data["business_message"]

        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        text = msg.get("text", "").strip().lower()

        if text == "usdt":
            send_payment(
                msg["chat"]["id"],
                msg["business_connection_id"]
            )

    # Normal Bot Messages
    elif "message" in data:

        msg = data["message"]

        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        text = msg.get("text", "").strip().lower()

        if text == "usdt":
            send_payment(msg["chat"]["id"])

    # Buttons
    elif "callback_query" in data:

        query = data["callback_query"]

        chat_id = query["message"]["chat"]["id"]

        business_connection_id = query["message"].get("business_connection_id")

        if query["data"] == "binance":

            send_uid(
                chat_id,
                "📋 Binance UID",
                BINANCE_UID,
                business_connection_id
            )

        elif query["data"] == "bybit":

            send_uid(
                chat_id,
                "📋 Bybit UID",
                BYBIT_UID,
                business_connection_id
            )

        telegram(
            "answerCallbackQuery",
            {
                "callback_query_id": query["id"]
            }
        )

    return "OK", 200
    if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
