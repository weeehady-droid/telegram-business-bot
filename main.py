from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]

replies = {
    "سعر": "سعر الاشتراك 100 جنيه",
    "واتس": "01000000000",
    "عنوان": "القاهرة"
}

def send(chat_id, text, business_connection_id=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if business_connection_id:
        data["business_connection_id"] = business_connection_id

    r = requests.post(url, json=data)
    print("Telegram response:", r.text)


@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(data)

    # Telegram Business
    if "business_message" in data:
        msg = data["business_message"]
        text = msg.get("text", "").strip()
        chat_id = msg["chat"]["id"]
        business_connection_id = msg["business_connection_id"]

        if text in replies:
            send(chat_id, replies[text], business_connection_id)

    # الرسائل العادية
    elif "message" in data:
        msg = data["message"]
        text = msg.get("text", "").strip()
        chat_id = msg["chat"]["id"]

        if text in replies:
            send(chat_id, replies[text])

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
