from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

replies = {
    "سعر": "سعر الاشتراك 100 جنيه",
    "واتس": "01000000000",
    "عنوان": "القاهرة"
}

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print(data)

    message = data.get("message")

    if message:
        text = message.get("text", "")
        chat_id = message["chat"]["id"]

        if text in replies:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": replies[text]
                }
            )

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
