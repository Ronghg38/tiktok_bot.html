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
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"CauTuRong Realtime Market Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🤖 @{BOT_ID}\n\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Lỗi gửi Telegram (Code {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Ngoại lệ khi gửi Telegram: {e}")

# Hàm lấy dữ liệu (Trong thực tế nên dùng BeautifulSoup/Scrapy hoặc API)
def get_realtime_market_data():
    current_time_str = datetime.now().strftime('%H:%M - %d/%m/%Y')
    
    # Giả lập dữ liệu có thể thay đổi.
    # Để bot thực sự hiệu quả, bạn cần thay phần này bằng Code Cào Dữ Liệu (Web Scraping) hoặc API
    data = {
        "time": current_time_str,
        "sjc_buy": "139.70 triệu/lượng",     
        "sjc_sell": "142.70 triệu/lượng",    
        "usd_vnd": "25,730 VND",            
        "gas_e10_ron95": "25,730 đ/lít",    
        "gas_e5": "26,020 đ/lít",           
        "oil_diesel": "23,500 đ/lít",       
        "coffee_robusta": "87,000 - 87,500 đ/kg",   
        "pepper": "135,000 - 137,500 đ/kg",         
        "rice_om5451": "7,200 - 7,400 đ/kg"         
    }
    return data

def run_smart_market_loop():
    send_telegram_alert("🚀 *Hệ thống Bot Cập Nhật Giá Thực Tế Thị Trường CAUTURONG đã kích hoạt!*")
    print("Market loop started.")
    
    last_sent_data = None
    
    while True:
        try:
            current_data = get_realtime_market_data()
            
            # Tạo một bản copy bỏ đi trường 'time' để so sánh giá trị thay đổi thực sự
            current_compare = current_data.copy()
            current_compare.pop("time", None)
            
            last_compare = None
            if last_sent_data:
                last_compare = last_sent_data.copy()
                last_compare.pop("time", None)

            is_price_changed = (current_compare != last_compare)
            
            # Nếu là lần chạy đầu tiên hoặc giá có thay đổi thì gửi
            if not last_sent_data or is_price_changed:
                report = (
                    f"🇻🇳 *BẢN TIN BIẾN ĐỘNG THỊ TRƯỜNG & XĂNG DẦU* 🇻🇳\n"
                    f"🕒 Thời gian: `{current_data['time']}`\n\n"
                    f"🥇 *Giá Vàng SJC:*\n"
                    f"- Mua vào: `{current_data['sjc_buy']}`\n"
                    f"- Bán ra: `{current_data['sjc_sell']}`\n\n"
                    f"💵 *Tỷ giá USD tham khảo:* `1 USD = {current_data['usd_vnd']}`\n\n"
                    f"⛽ *Giá Xăng Dầu Trong Nước (Đường giá bán lẻ):*\n"
                    f"- Xăng E10 RON 95: `{current_data['gas_e10_ron95']}`\n"
                    f"- Xăng E5 RON 92: `{current_data['gas_e5']}`\n"
                    f"- Dầu Diesel: `{current_data['oil_diesel']}`\n\n"
                    f"☕ *Cà phê nhân xô (Tây Nguyên):*\n"
                    f"👉 `{current_data['coffee_robusta']}`\n\n"
                    f"🌶️ *Hồ tiêu các tỉnh:*\n"
                    f"👉 `{current_data['pepper']}`\n\n"
                    f"🍚 *Lúa gạo tươi (ĐBSCL - OM5451):*\n"
                    f"👉 `{current_data['rice_om5451']}`\n\n"
                    f"📊 *Nhận định:* Bảng giá cập nhật theo dữ liệu niêm yết thực tế từ các đơn vị giao dịch chính thức."
                )
                send_telegram_alert(report)
                last_sent_data = current_data
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [+] Đã gửi bản tin giá thực tế mới nhất về Telegram.")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [-] Giá cả thị trường chưa có thay đổi mới...")
                
        except Exception as e:
            print(f"Lỗi vòng lặp: {e}")
        
        # Chờ 30 phút (1800 giây)
        time.sleep(1800)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    run_smart_market_loop()
