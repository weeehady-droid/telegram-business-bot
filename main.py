@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(data)

    # رسائل Business
    if "business_message" in data:
        msg = data["business_message"]
        text = msg.get("text", "")
        chat_id = msg["chat"]["id"]

        if text in replies:
            send(chat_id, replies[text])

    # الرسائل العادية
    elif "message" in data:
        msg = data["message"]
        text = msg.get("text", "")
        chat_id = msg["chat"]["id"]

        if text in replies:
            send(chat_id, replies[text])

    return "ok"
