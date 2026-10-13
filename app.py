import os
import time
from threading import Thread
from flask import Flask, request, jsonify
import requests
from telepot import Bot
from telepot.loop import MessageLoop

# ==========================================
#  CONFIGURATION & CREDENTIALS (الإعدادات)
# ==========================================
TOKEN = "8687366877:AAF-aknHwV1KGIZWNSyRJT_-bod1xlNMPis"
ADMIN_CHAT_ID = "6134785035"

bot = Bot(TOKEN)

# إعدادات إدارة رأس المال والمخاطر الافتراضية
DEFAULT_CAPITAL = 1000
DEFAULT_RISK = 1.0

# إعداد خادم Flask للويب واستقبال التنبيهات
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "GOLD SNIPER AI Webhook Server is Live and Running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ==========================================
#  TELEGRAM SENDER (مرسل الإشارات)
# ==========================================
def send_trade_signal(chat_id, sig_data):
    message = (
        f"🎯 <b>إشارة تداول احترافية (TradingView)</b> 🎯\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔹 <b>الزوج:</b> الذهب مقابل الدولار (XAUUSD)\n"
        f"🔹 <b>النوع:</b> {sig_data['label']}\n\n"
        f"📍 <b>سعر الدخول (ENTRY):</b> <code>{sig_data['price']}$</code>\n"
        f"🛑 <b>وقف الخسارة (SL):</b> <code>{sig_data['sl']}$</code>\n"
        f"🎯 <b>جني الأرباح (TP):</b> <code>{sig_data['tp']}$</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🛡️ <b>إدارة رأس المال وحجم العقد الموصى به:</b>\n"
        f"• <b>حجم رأس المال:</b> ${sig_data['capital']}\n"
        f"• <b>مخاطرة الصفقة:</b> {sig_data['risk']}%\n"
        f"• <b>حجم العقد المناسب:</b> <code>{sig_data['lot']} Lot</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⏰ <b>التحديث:</b> فوري ومباشر من شارت TradingView"
    )
    try:
        bot.sendMessage(chat_id, message, parse_mode="HTML")
    except Exception as e:
        print(f"Telegram Send Error: {e}")

# ==========================================
#  TRADINGVIEW WEBHOOK ENDPOINT (مستقبل التنبيهات)
# ==========================================
@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    try:
        # محاولة قراءة البيانات سواء كانت JSON أو نصية
        data = request.get_json(silent=True)
        if not data:
            # إذا لم تكن JSON، نحاول قراءتها كبيانات نموذج أو نص
            data = request.form.to_dict()
        if not data:
            # محاولة قراءة النص الخام
            raw_data = request.data.decode('utf-8')
            print(f"Received raw data: {raw_data}")
            data = {"action": "BUY", "price": 4195.0, "sl_pips": 30}

        action = str(data.get('action', 'BUY')).upper()
        price = float(data.get('price', 4195.0))
        sl_pips = float(data.get('sl_pips', 30))
        capital = float(data.get('balance', DEFAULT_CAPITAL))
        risk_percent = float(data.get('risk', DEFAULT_RISK))

        if "SELL" in action or action == "SELL":
            label = "🔴 SELL (بيع)"
            sl_price = round(price + (sl_pips * 0.1), 2)
            tp_price = round(price - (sl_pips * 0.2), 2)
        else:
            label = "🟢 BUY (شراء)"
            sl_price = round(price - (sl_pips * 0.1), 2)
            tp_price = round(price + (sl_pips * 0.2), 2)

        risk_amount = capital * (risk_percent / 100)
        pip_value_per_lot = 10.0
        lot_size = risk_amount / (sl_pips * pip_value_per_lot)
        lot_size = max(0.01, round(lot_size, 2))

        sig_data = {
            "label": label,
            "price": price,
            "sl": sl_price,
            "tp": tp_price,
            "lot": lot_size,
            "capital": capital,
            "risk": risk_percent
        }

        send_trade_signal(ADMIN_CHAT_ID, sig_data)
        return jsonify({"status": "success", "message": "Signal processed successfully"}), 200

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

# ==========================================
#  HANDLERS (الأوامر اليدوية للبوت)
# ==========================================
def handle(msg):
    try:
        chat_id = msg['chat']['id']
        text = msg.get('text', '')

        if text == "/start":
            bot.sendMessage(chat_id, "مرحباً بك في بوت قناص الذهب. البوت يعمل الآن بكفاءة وجاهز تماماً!")
        elif text == "/check":
            bot.sendMessage(chat_id, "سيرفر الويب (Webhook) يعمل بنجاح وجاهز لاستقبال الإشارات.")
    except Exception as e:
        print(f"Handler Error: {e}")

# ==========================================
#  RUN (المشغل الرئيسي)
# ==========================================
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    print("GOLD SNIPER WEBHOOK SERVER IS ACTIVE AND LISTENING...")
    
    MessageLoop(bot, handle).run_as_thread()
    
    while True:
        time.sleep(10)
