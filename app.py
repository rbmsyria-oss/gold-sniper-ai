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
        f"⏰ <b>التحديث:</b> فوري ومباشر من شارت TradingView لعام 2026"
    )
    bot.sendMessage(chat_id, message, parse_mode="HTML")

# ==========================================
#  TRADINGVIEW WEBHOOK ENDPOINT (مستقبل التنبيهات)
# ==========================================
@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    try:
        data = request.get_json(silent=True) or {}
        
        # استخراج البيانات القادمة من تنبيه تريدنج فيو
        action = data.get('action', 'BUY').upper()  # BUY أو SELL
        price = float(data.get('price', 4195.0))
        sl_pips = float(data.get('sl_pips', 30))      # عدد النقاط لوقف الخسارة
        capital = float(data.get('balance', DEFAULT_CAPITAL))
        risk_percent = float(data.get('risk', DEFAULT_RISK))

        # حساب الأسعار والأهداف بناءً على اتجاه الصفقة
        if action == "BUY":
            label = "🟢 BUY (شراء)"
            sl_price = round(price - (sl_pips * 0.1), 2)
            tp_price = round(price + (sl_pips * 0.2), 2) # هدف بضعف مسافة الوقف (Risk:Reward 1:2)
        else:
            label = "🔴 SELL (بيع)"
            sl_price = round(price + (sl_pips * 0.1), 2)
            tp_price = round(price - (sl_pips * 0.2), 2)

        # حساب حجم العقد بناءً على إدارة المخاطر
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

        # إرسال التنبيه إلى المسؤول عبر تليجرام
        send_trade_signal(ADMIN_CHAT_ID, sig_data)
        
        return jsonify({"status": "success", "message": "Signal processed successfully"}), 200

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

# ==========================================
#  HANDLERS (الأوامر اليدوية للبوت)
# ==========================================
def handle(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":
        bot.sendMessage(chat_id, "مرحباً بك في بوت قناص الذهب المربوط بـ TradingView.\n\nالبوت الآن جاهز لاستقبال التنبيهات الفورية من الشارت وإرسالها إليك مباشرة!")

    if text == "/check":
        bot.sendMessage(chat_id, "سيرفر الويب (Webhook) يعمل بنجاح وجاهز لاستقبال إشارات TradingView الفورية.")

# ==========================================
#  RUN (المشغل الرئيسي)
# ==========================================
if __name__ == "__main__":
    try: 
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    except: 
        pass

    # تشغيل خادم الويب لاستقبال التنبيهات بالخلفية
    Thread(target=run_web, daemon=True).start()
    
    print("GOLD SNIPER WEBHOOK SERVER IS ACTIVE AND LISTENING...")
    MessageLoop(bot, handle).run_as_thread()
    
    while True:
        time.sleep(10)
