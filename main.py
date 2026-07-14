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
