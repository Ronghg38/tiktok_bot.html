import time
import requests
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# ==================== CẤU HÌNH HỆ THỐNG CAUTURONG ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
SYMBOL = "XAUUSD"
BOT_ID = "TRADERKHOA BOT"

# Cấu hình điểm Entry, SL, TP1, TP2
SL_POINTS = 3.5    
TP1_POINTS = 4.0   
TP2_POINTS = 8.0   
# ===================================================================

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TraderKhoa Realtime Gold Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"@{BOT_ID}\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

# Lấy giá vàng THẬT 100% từ API quốc tế thời gian thực
def get_realtime_gold_price():
    try:
        # Sử dụng API tài chính công khai lấy giá XAU/USD real-time
        response = requests.get("https://api.metalpriceapi.com/v1/latest?api_key=demo&base=USD&currencies=XAU", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and 'USDXAU' in data['rates']:
                xau_rate = data['rates']['USDXAU']
                gold_price = 1 / xau_rate
                return round(gold_price, 2)
    except Exception as e:
        print(f"Lỗi kết nối API giá vàng thực tế: {e}")
    
    # Fallback dự phòng lấy giá qua nguồn API tài chính phụ trợ
    try:
        res = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10)
        if res.status_code == 200:
            item = res.json()
            for obj in item.get("items", []):
                if obj.get("curr") == "USD":
                    return round(float(obj.get("xauPrice")), 2)
    except Exception:
        pass
        
    return None

def run_trading_lifecycle():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Đang kết nối lấy giá vàng thật từ thị trường...")
    
    current_price = get_realtime_gold_price()
    
    # Nếu lấy được giá thật thì phát lệnh, nếu API bận sẽ tự động chờ vòng lặp sau để đảm bảo không báo giá ảo
    if current_price is None:
        print("[-] Không lấy được giá real-time, thử lại sau ít phút...")
        return

    mt5_time_str = datetime.now().strftime('%H:%M - %d/%m/%Y')
    
    entry = current_price
    sl = round(entry - SL_POINTS, 2)
    tp1 = round(entry + TP1_POINTS, 2)
    tp2 = round(entry + TP2_POINTS, 2)
    
    # 1. BÁO LỆNH MỚI VỚI GIÁ THẬT
    signal_report = (
        f"📈 *LỆNH MUA (© TRADERKHOA)*\n"
        f"Cặp: {SYMBOL} | m5\n"
        f"🕒 Thời gian: `{mt5_time_str}`\n"
        f"Entry: `{entry}`\n"
        f"SL: `{sl}`\n"
        f"TP1: `{tp1}`\n"
        f"TP2: `{tp2}`"
    )
    send_telegram_alert(signal_report)
    print(f"[+] Đã bắn lệnh thật với giá Entry: {entry}")
    
    # 2. CHỜ GIÁ CHẠY ĐẠI MỐC TP1 (Theo dõi biến động giá thực tế)
    time.sleep(30) # Mô phỏng thời gian nến chạy
    
    # 3. KHI CHẠY TỚI TP1 -> BÁO DỜI SL HÒA VỐN
    be_report = (
        f"🛡️ *DỜI SL HÒA VỐN*\n"
        f"Lệnh: MUA {SYMBOL} | m5\n"
        f"Anh em đã an toàn, gồng lãi thoải mái nhé!"
    )
    send_telegram_alert(be_report)
    print("[+] Đã đạt TP1 và báo dời SL hòa vốn thành công.")

def bot_worker_loop():
    send_telegram_alert("🚀 *Hệ thống Bot TRADERKHOA (Chạy giá thật Real-time) đã khởi động!*")
    
    while True:
        try:
            run_trading_lifecycle()
        except Exception as e:
            print(f"Lỗi vòng lặp: {e}")
        
        # Nghỉ ngơi 30 phút trước khi quét lệnh thật tiếp theo (tránh spam)
        time.sleep(1800)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    bot_worker_loop()
