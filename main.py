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
 
# أزرار نسخ سريعة تظهر تحت الرسالة (اختياري لكل كلمة مفتاحية)
keyboards = {
    "كاش": {
        "inline_keyboard": [
            [{"text": "نسخ فودافون كاش 🔴", "copy_text": {"text": "01096352480"}}],
            [{"text": "نسخ انستاباي 💸", "copy_text": {"text": "01123512580"}}]
        ]
    }
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
 
 
def send(chat_id, text, business_connection_id=None, reply_markup=None):
    # يظهر "بيكتب..." الأول قبل ما يبعت الرد
    send_typing(chat_id, business_connection_id)
    time.sleep(TYPING_DELAY_SECONDS)
 
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if business_connection_id:
        payload["business_connection_id"] = business_connection_id
    if reply_markup:
        payload["reply_markup"] = reply_markup
 
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json=payload
    )
    print(r.text)
 
 
@app.route("/")
def home():
    return "Bot is running!"
 
 
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
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
            send(chat_id, replies[text], business_connection_id, keyboards.get(text))
 
    elif "message" in data:
        msg = data["message"]
        # يرد على رسائلك أنت فقط
        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200
 
        text = msg.get("text", "").strip().lower()
        chat_id = msg["chat"]["id"]
 
        if text in replies:
            send(chat_id, replies[text], reply_markup=keyboards.get(text))
 
    return "OK", 200
 
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
