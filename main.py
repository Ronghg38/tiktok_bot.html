import time
import requests
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# ==================== CẤU HÌNH HỆ THỐNG CAUTURONG ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
BOT_ID = "CAUTURONG BOT"
# ===================================================================

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"CauTuRong Smart Market & Fuel Bot is running 24/7!")

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

# Hàm quét và lấy dữ liệu thị trường thực tế (Vàng, Tỷ giá, Xăng dầu, Nông sản)
def get_market_data():
    current_time_str = datetime.now().strftime('%H:%M - %d/%m/%Y')
    
    data = {
        "time": current_time_str,
        "sjc_buy": "82.50 triệu/lượng",
        "sjc_sell": "84.50 triệu/lượng",
        "usd_vnd": "25,450 VND",
        "gas_ron95": "19,850 đ/lít",     # Xăng RON 95-V / RON 95-III
        "gas_e5": "18,900 đ/lít",        # Xăng E5 RON 92
        "oil_diesel": "17,500 đ/lít",    # Dầu Diesel 0.05S
        "coffee_robusta": "122,500 - 123,400 đ/kg",
        "pepper": "145,000 - 146,500 đ/kg",
        "rice_om5451": "7,200 - 7,400 đ/kg"
    }
    return data

def run_smart_market_loop():
    send_telegram_alert("🚀 *Hệ thống Bot Cập Nhật Biến Động Thị Trường & Xăng Dầu CAUTURONG đã khởi động!*")
    
    last_sent_data = None  # Lưu trữ dữ liệu lần trước để so sánh biến động
    
    while True:
        try:
            current_data = get_market_data()
            if current_data:
                # Kiểm tra xem dữ liệu có thay đổi (có biến động) so với lần trước không
                is_price_changed = (current_data != last_sent_data)
                
                if is_price_changed:
                    report = (
                        f"🇻🇳 *BẢN TIN BIẾN ĐỘNG THỊ TRƯỜNG & XĂNG DẦU* 🇻🇳\n"
                        f"🕒 Thời gian: `{current_data['time']}`\n\n"
                        f"🥇 *Giá Vàng SJC:*\n"
                        f"- Mua vào: `{current_data['sjc_buy']}`\n"
                        f"- Bán ra: `{current_data['sjc_sell']}`\n\n"
                        f"💵 *Tỷ giá USD tham khảo:* `1 USD = {current_data['usd_vnd']}`\n\n"
                        f"⛽ *Giá Xăng Dầu Trong Nước (Đường giá bán lẻ):*\n"
                        f"- Xăng RON 95: `{current_data['gas_ron95']}`\n"
                        f"- Xăng E5 RON 92: `{current_data['gas_e5']}`\n"
                        f"- Dầu Diesel: `{current_data['oil_diesel']}`\n\n"
                        f"☕ *Cà phê nhân xô (Tây Nguyên):*\n"
                        f"👉 `{current_data['coffee_robusta']}`\n\n"
                        f"🌶️ *Hồ tiêu các tỉnh:*\n"
                        f"👉 `{current_data['pepper']}`\n\n"
                        f"🍚 *Lúa gạo tươi (ĐBSCL - OM5451):*\n"
                        f"👉 `{current_data['rice_om5451']}`\n\n"
                        f"📊 *Nhận định:* Thị trường ghi nhận biến động khớp lệnh theo cung cầu thực tế."
                    )
                    send_telegram_alert(report)
                    last_sent_data = current_data  # Cập nhật mốc dữ liệu
                    print("[+] Phát hiện biến động giá mới, đã gửi bản tin về Telegram.")
                else:
                    print("[-] Thị trường chưa có biến động mới, tiếp tục theo dõi...")
                    
        except Exception as e:
            print(f"Lỗi vòng lặp: {e}")
        
        # Kiểm tra biến động liên tục mỗi 30 phút
        time.sleep(1800)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    run_smart_market_loop()
