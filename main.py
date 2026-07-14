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

def send(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

@app.route("/")
def home():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(data)

    if "business_message" in data:
        msg = data["business_message"]
        text = msg.get("text", "")
        chat_id = msg["chat"]["id"]

        if text in replies:
            send(chat_id, replies[text])

    elif "message" in data:
        msg = data["message"]
        text = msg.get("text", "")
        chat_id = msg["chat"]["id"]

        if text in replies:
            send(chat_id, replies[text])

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
