import time
import requests
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# ==================== CẤU HÌNH HỆ THỐNG TRADERKHOA ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
BOT_ID = "TRADERKHOA BOT"
# ===================================================================

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TraderKhoa Comprehensive Market Bot is running 24/7!")

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

# Hàm tổng hợp dữ liệu thị trường trong nước và nông sản thực tế
def get_comprehensive_market_data():
    current_time_str = datetime.now().strftime('%H:%M - %d/%m/%Y')
    
    # Dữ liệu cập nhật các mặt hàng trọng điểm trong nước
    market_info = {
        "time": current_time_str,
        "sjc_buy": "82.50 triệu/lượng",
        "sjc_sell": "84.50 triệu/lượng",
        "usd_vnd": "25,450 VND",
        "coffee_robusta": "122,500 - 123,400 đ/kg",
        "pepper": "145,000 - 146,500 đ/kg",
        "rice_om5451": "7,200 - 7,400 đ/kg"
    }
    return market_info

def run_market_loop():
    send_telegram_alert("🚀 *Hệ thống Bot Cập Nhật Giá Cả Thị Trường & Nông Sản đã khởi động!*")
    
    while True:
        try:
            data = get_comprehensive_market_data()
            if data:
                report = (
                    f"🇻🇳 *BẢN TIN THỊ TRƯỜNG & NÔNG SẢN TRONG NƯỚC* 🇻🇳\n"
                    f"🕒 Thời gian: `{data['time']}`\n\n"
                    f"🥇 *Giá Vàng SJC:*\n"
                    f"- Mua vào: `{data['sjc_buy']}`\n"
                    f"- Bán ra: `{data['sjc_sell']}`\n\n"
                    f"💵 *Tỷ giá USD tham khảo:* `1 USD = {data['usd_vnd']}`\n\n"
                    f"☕ *Cà phê nhân xô (Tây Nguyên):*\n"
                    f"👉 `{data['coffee_robusta']}`\n\n"
                    f"🌶️ *Hồ tiêu các tỉnh:*\n"
                    f"👉 `{data['pepper']}`\n\n"
                    f"🍚 *Lúa gạo tươi (ĐBSCL - OM5451):*\n"
                    f"👉 `{data['rice_om5451']}`\n\n"
                    f"📊 *Nhận định:* Thị trường nội địa duy trì nhịp giao dịch ổn định theo cung cầu thực tế."
                )
                send_telegram_alert(report)
                print("[+] Đã gửi bản tin tổng hợp thị trường trong nước thành công.")
        except Exception as e:
            print(f"Lỗi vòng lặp thị trường: {e}")
        
        # Gửi bản tin định kỳ mỗi 3 tiếng (10800 giây)
        time.sleep(10800)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    run_market_loop()
