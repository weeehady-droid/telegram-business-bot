from flask import Flask, request
import requests
import os
import time
 
app = Flask(__name__)
TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = 5260085571
TYPING_DELAY_SECONDS = 2  # قد إيه يفضل شكله بيكتب قبل ما يبعت الرد
 
replies = {
    "usdt": """<blockquote><b><i>Enter and click on any wallet to be copied <tg-emoji emoji-id="5332668748044204575">👆</tg-emoji></i></b></blockquote>
 
<blockquote><b><i>- Binance <tg-emoji emoji-id="5420232672964275159">🟡</tg-emoji> : (<code>1156755586</code>)</i></b></blockquote>
 
<blockquote><b><i>- Bybit <tg-emoji emoji-id="5433900293987261516">🟠</tg-emoji> : (<code>523496990</code>)</i></b></blockquote>
 
<blockquote><b><i><tg-emoji emoji-id="5832251986635920010">📸</tg-emoji> Don't forget to take a screenshot
of the transaction you made.</i></b></blockquote>""",
 
    "كاش": """<blockquote><b><i>Enter and click on any wallet to be copied <tg-emoji emoji-id="5332668748044204575">👛</tg-emoji></i></b></blockquote>
 
<blockquote><b><i>- Vodafone Cash <tg-emoji emoji-id="5836910638877643137">🔴</tg-emoji> : (<code>01096352480</code>)</i></b></blockquote>
 
<blockquote><b><i>- Instapay <tg-emoji emoji-id="5895429645595055968">💸</tg-emoji> : (<code>01123512580</code>)</i></b></blockquote>
 
<blockquote><b><i><tg-emoji emoji-id="5832251986635920010">📸</tg-emoji> Don't forget to take a screenshot
of the transaction you made.</i></b></blockquote>"""
}
 
 
def send_typing(chat_id, business_connection_id=None):
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    if business_connection_id:
        payload["business_connection_id"] = business_connection_id
 
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendChatAction",
        json=payload
    )
 
 
def edit_message(chat_id, message_id, text, business_connection_id=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if business_connection_id:
        payload["business_connection_id"] = business_connection_id
 
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/editMessageText",
        json=payload
    )
    print(r.text)
 
 
def send(chat_id, text, business_connection_id=None):
    # الرسالة مقسّمة بسطر فاضي بين كل بلوك (blockquote)
    blocks = text.split("\n\n")
 
    # يظهر "بيكتب..." شوية الأول
    send_typing(chat_id, business_connection_id)
    time.sleep(TYPING_DELAY_SECONDS)
 
    # يبعت أول بلوك بس
    payload = {
        "chat_id": chat_id,
        "text": blocks[0],
        "parse_mode": "HTML"
    }
    if business_connection_id:
        payload["business_connection_id"] = business_connection_id
 
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json=payload
    )
    print(r.text)
 
    result = r.json()
    if not result.get("ok"):
        return
    message_id = result["result"]["message_id"]
 
