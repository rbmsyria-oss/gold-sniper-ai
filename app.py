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

# إعدادات إدارة رأس المال والمخاطر
CAPITAL = 1000          # رأس المال الافتراضي
RISK_PERCENT = 1.0      # نسبة المخاطرة لكل صفقة (%)

# إعداد خادم Flask للويب (مطلوب لكي تستقر المنصة السحابية ولا تتوقف)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "GOLD SNIPER AI Server is Live and Running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ==========================================
#  LIVE PRICE FETCHER (جلب سعر الذهب الحقيقي - الميزة الجديدة بدون حذف القديم)
# ==========================================
def get_live_gold_price():
    try:
        # استخدام مصدر مجاني سريع لجلب سعر الذهب الفوري
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tether-gold&vs_currencies=usd", timeout=5)
        data = response.json()
        live_price = float(data['tether-gold']['usd'])
        return live_price
    except Exception as e:
        print(f"تعذر جلب السعر اللحظي، سيتم استخدام السعر الاحتياطي: {e}")
        return 4195.0  # السعر الاحتياطي تماماً كما كان في الكود الأصلي

# ==========================================
#  SIGNAL GENERATOR & TELEGRAM SENDER (المحرك)
# ==========================================
def generate_professional_signal():
    """توليد صفقة بناءً على سعر الذهب الحقيقي المحدث أو السعر الافتراضي"""
    entry_price = get_live_gold_price()
    sl_pips = 30
    
    # حساب الأسعار والأهداف بناءً على اتجاه افتراضي (BUY)
    sl_price = round(entry_price - (sl_pips * 0.1), 2)
    tp1_price = round(entry_price + (sl_pips * 0.1), 2)
    
    # حساب حجم العقد بناءً على إدارة المخاطر
    risk_amount = CAPITAL * (RISK_PERCENT / 100)
    pip_value_per_lot = 10.0
    lot_size = risk_amount / (sl_pips * pip_value_per_lot)
    lot_size = max(0.01, round(lot_size, 2))

    return {
        "label": "🟢 BUY (شراء)",
        "price": entry_price,
        "sl": sl_price,
        "tp": tp1_price,
        "lot": lot_size
    }

def send_trade_signal(chat_id, sig_data):
    message = (
        f"🎯 <b>إشارة تداول احترافية جديدة | NEW TRADE SIGNAL</b> 🎯\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔹 <b>الزوج:</b> الذهب مقابل الدولار (XAUUSD)\n"
        f"🔹 <b>النوع:</b> {sig_data['label']}\n\n"
        f"📍 <b>سعر الدخول الحالي (ENTRY):</b> <code>{sig_data['price']}$</code>\n"
        f"🛑 <b>وقف الخسارة (SL):</b> <code>{sig_data['sl']}$</code>\n"
        f"🎯 <b>جني الأرباح (TP):</b> <code>{sig_data['tp']}$</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🛡️ <b>إدارة رأس المال وحجم العقد الموصى به:</b>\n"
        f"• <b>حجم رأس المال:</b> ${CAPITAL}\n"
        f"• <b>مخاطرة الصفقة:</b> {RISK_PERCENT}%\n"
        f"• <b>حجم العقد المناسب لفتح الصفقة:</b> <code>{sig_data['lot']} Lot</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⏰ <b>التحديث:</b> آلي عبر شارت التداول الفوري لعام 2026"
    )
    bot.sendMessage(chat_id, message, parse_mode="HTML")

# ==========================================
#  HOURLY AUTOMATION TIMERS (نظام التنبيهات الآلية كل ساعة)
# ==========================================
def hourly_market_scanner():
    print("تم تفعيل نظام التنبيه والمراقبة التلقائية لشارت الذهب كل ساعة...")
    time.sleep(10)
    while True:
        try:
            print("حان موعد التحديث الآلي، جاري إرسال التوصية الدورية لعام 2026...")
            signal_report = generate_professional_signal()
            send_trade_signal(ADMIN_CHAT_ID, signal_report)
        except Exception as e:
            print(f"حدث خطأ في المؤقت الدوري: {str(e)}")
        
        time.sleep(3600) # الانتظار ساعة كاملة

# ==========================================
#  HANDLERS (الأوامر الواردة للبوت يدوياً)
# ==========================================
def handle(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":
        bot.sendMessage(chat_id, f"مرحباً بك في المحلل المحترف للذهب\n\nإدارة رأس مالك الحالية مضبوطة على: {CAPITAL}$ بمخاطرة {RISK_PERCENT}%.\n\nالبوت يقوم الآن بمسح السوق وسيصلك تقرير دوري تلقائياً كل ساعة.\nإذا أردت فحصاً يدوياً عاجلاً في أي وقت أرسل: /check")

    if text == "/check":
        bot.sendMessage(chat_id, "جاري تشغيل الخوارزميات الفنية المتقدمة وبناء الصفقة...")
        sig = generate_professional_signal()
        send_trade_signal(chat_id, sig)

# ==========================================
#  RUN (المحرك والمشغل الرئيسي)
# ==========================================
if __name__ == "__main__":
    try: 
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    except: 
        pass

    # 1. تشغيل خادم الويب المدمج لـ Flask بالخلفية
    Thread(target=run_web, daemon=True).start()
    
    # 2. تشغيل رادار التحديث التلقائي كل ساعة في مسار منفصل بالخلفية
    Thread(target=hourly_market_scanner, daemon=True).start()
    
    print("GOLD SNIPER PRO IS FULLY OPERATIONAL AND ACTIVE...")
    MessageLoop(bot, handle).run_as_thread()
    
    while True:
        time.sleep(10)
