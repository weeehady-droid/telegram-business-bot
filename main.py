from flask import Flask, request
import requests
import os
import re
import json
import time
import threading

app = Flask(__name__)
TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = 5260085571

DEBTS_FILE = "debts.json"
DEFAULT_INTERVAL_DAYS = 1
REMINDER_CHECK_SECONDS = 600  # يفحص كل 10 دقايق لو في تذكير مستحق

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
    "usdt": {
        "inline_keyboard": [
            [{"text": "Binance", "copy_text": {"text": "1156755586"}, "icon_custom_emoji_id": "5420232672964275159", "style": "danger"}],
            [{"text": "Bybit", "copy_text": {"text": "523496990"}, "icon_custom_emoji_id": "5433900293987261516", "style": "success"}]
        ]
    },
    "كاش": {
        "inline_keyboard": [
            [{"text": "Vodafone Cash", "copy_text": {"text": "01096352480"}, "style": "danger"}],
            [{"text": "Instapay", "copy_text": {"text": "01123512580"}, "style": "primary"}]
        ]
    }
}


# رسائل مخصصة لموضوع الدين بس (منفصلة عن ردود usdt / كاش الأصلية)

def debt_message_egp(amount):
    return (
        f"<blockquote><b><i>⏰ تذكير: عليك {amount} جنيه</i></b></blockquote>\n\n"
        f"<blockquote><b><i>برجاء السداد في أقرب وقت 🙏</i></b></blockquote>\n\n"
        f"<blockquote><i>ملحوظة: ده بوت تذكير تلقائي، وهيتم إرسال الرسالة دي تلقائيًا كل 24 ساعة لحد ما يتم السداد.</i></blockquote>"
    )


def debt_message_usd(amount):
    return (
        f"<blockquote><b><i>⏰ Reminder: You have a pending payment of {amount}$</i></b></blockquote>\n\n"
        f"<blockquote><b><i>Please settle it as soon as possible 🙏</i></b></blockquote>\n\n"
        f"<blockquote><i>Note: This is an automated reminder bot, and this message will be sent automatically every 24 hours until payment is settled.</i></blockquote>"
    )


# ---------- تخزين الديون ----------

def load_debts():
    if os.path.exists(DEBTS_FILE):
        try:
            with open(DEBTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_debts():
    with open(DEBTS_FILE, "w", encoding="utf-8") as f:
        json.dump(debts, f, ensure_ascii=False, indent=2)


debts = load_debts()
debts_lock = threading.Lock()


# ---------- إرسال الرسائل ----------

def send(chat_id, text, business_connection_id=None, reply_markup=None):
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


# ---------- أوامر تتبع الديون (بتتكتب جوه محادثة الشخص نفسه) ----------

def handle_debt_commands(text, chat_id, business_connection_id=None):
    chat_key = str(chat_id)

    # عليك <مبلغ>  -> جنيه (كاش)
    m = re.match(r'^عليك\s+(\d+(?:\.\d+)?)$', text)
    if m:
        amount = float(m.group(1))
        with debts_lock:
            entry = debts.get(chat_key, {
                "amount_egp": 0,
                "amount_usd": 0,
                "interval_days": DEFAULT_INTERVAL_DAYS,
                "last_reminder": time.time()
            })
            entry["amount_egp"] = entry.get("amount_egp", 0) + amount
            entry["business_connection_id"] = business_connection_id
            entry.setdefault("interval_days", DEFAULT_INTERVAL_DAYS)
            entry.setdefault("last_reminder", time.time())
            debts[chat_key] = entry
            save_debts()

        send(chat_id, debt_message_egp(entry["amount_egp"]), business_connection_id, keyboards.get("كاش"))
        return True

    # payment <مبلغ>  -> دولار (usdt)
    m = re.match(r'^payment\s+(\d+(?:\.\d+)?)$', text, re.IGNORECASE)
    if m:
        amount = float(m.group(1))
        with debts_lock:
            entry = debts.get(chat_key, {
                "amount_egp": 0,
                "amount_usd": 0,
                "interval_days": DEFAULT_INTERVAL_DAYS,
                "last_reminder": time.time()
            })
            entry["amount_usd"] = entry.get("amount_usd", 0) + amount
            entry["business_connection_id"] = business_connection_id
            entry.setdefault("interval_days", DEFAULT_INTERVAL_DAYS)
            entry.setdefault("last_reminder", time.time())
            debts[chat_key] = entry
            save_debts()

        send(chat_id, debt_message_usd(entry["amount_usd"]), business_connection_id, keyboards.get("usdt"))
        return True

    # اتسدد
    if text == "اتسدد":
        with debts_lock:
            if chat_key in debts:
                del debts[chat_key]
                save_debts()
        return True

    # payment clear -> يصفر الدولار بس
    if text.lower() == "payment clear":
        with debts_lock:
            if chat_key in debts:
                debts[chat_key]["amount_usd"] = 0
                if debts[chat_key].get("amount_egp", 0) <= 0:
                    del debts[chat_key]
                save_debts()
        return True

    # كل <رقم> يوم
    m2 = re.match(r'^كل\s+(\d+)\s+يوم$', text)
    if m2:
        days = int(m2.group(1))
        with debts_lock:
            entry = debts.get(chat_key, {"amount": 0, "last_reminder": time.time()})
            entry["interval_days"] = days
            entry["business_connection_id"] = business_connection_id
            debts[chat_key] = entry
            save_debts()
        return True

    return False


# ---------- خيط خلفي بيبعت التذكيرات ----------

def reminder_loop():
    while True:
        now = time.time()
        with debts_lock:
            changed = False
            for chat_key, info in list(debts.items()):
                egp = info.get("amount_egp", 0)
                usd = info.get("amount_usd", 0)
                if egp <= 0 and usd <= 0:
                    continue
                interval_seconds = info.get("interval_days", DEFAULT_INTERVAL_DAYS) * 86400
                last = info.get("last_reminder", 0)
                if now - last >= interval_seconds:
                    try:
                        if egp > 0:
                            send(int(chat_key), debt_message_egp(egp), info.get("business_connection_id"), keyboards.get("كاش"))
                        if usd > 0:
                            send(int(chat_key), debt_message_usd(usd), info.get("business_connection_id"), keyboards.get("usdt"))
                    except Exception as e:
                        print("reminder send error:", e)
                    info["last_reminder"] = now
                    changed = True
            if changed:
                save_debts()
        time.sleep(REMINDER_CHECK_SECONDS)


threading.Thread(target=reminder_loop, daemon=True).start()


@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print(data)

    if "business_message" in data:
        msg = data["business_message"]
        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        raw_text = msg.get("text", "").strip()
        text = raw_text.lower()
        chat_id = msg["chat"]["id"]
        business_connection_id = msg["business_connection_id"]

        # أوامر الديون (عليك بترد برسالة الدفع المناسبة، اتسدد بصمت)
        if handle_debt_commands(raw_text, chat_id, business_connection_id):
            return "OK", 200

        if text in replies:
            send(chat_id, replies[text], business_connection_id, keyboards.get(text))

    elif "message" in data:
        msg = data["message"]
        if msg.get("from", {}).get("id") != OWNER_ID:
            return "OK", 200

        raw_text = msg.get("text", "").strip()
        text = raw_text.lower()
        chat_id = msg["chat"]["id"]

        # قائمة الديون - بس في المحادثة الخاصة بينك وبين البوت
        if raw_text == "الديون":
            with debts_lock:
                if not debts:
                    send(chat_id, "مفيش حد عليه فلوس دلوقتي ✅")
                else:
                    lines = ["<b>الديون الحالية:</b>"]
                    for chat_key, info in debts.items():
                        egp = info.get("amount_egp", 0)
                        usd = info.get("amount_usd", 0)
                        lines.append(
                            f"- Chat {chat_key} : {egp} ج / {usd}$ "
                            f"(كل {info.get('interval_days', DEFAULT_INTERVAL_DAYS)} يوم)"
                        )
                    send(chat_id, "\n".join(lines))
            return "OK", 200

        if text in replies:
            send(chat_id, replies[text], reply_markup=keyboards.get(text))

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
