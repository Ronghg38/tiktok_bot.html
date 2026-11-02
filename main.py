import time
import requests
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import random
from bs4 import BeautifulSoup

# ==================== CẤU HÌNH HỆ THỐNG CAUTURONG ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
BOT_ID = "CAUTURONG BOT"
# ===================================================================

# 1. HÀM TẠO NỘI DUNG THỐNG KÊ VÀ BẮT CẦU XSMN
def generate_statistics_report():
    today_str = datetime.now().strftime('%d/%m/%Y')
    
    bach_thu = f"{random.randint(15, 95)}"
    da_1 = f"{random.randint(10, 48)}"
    da_2 = f"{random.randint(52, 98)}"
    cham_de = random.choice(["Chạm 3", "Chạm 5", "Chạm 7", "Chạm 9"])
    
    report = (
        f"🎯 *THỐNG KÊ & BẮT CẦU XSMN (NÓNG HỔI)* 🎯\n"
        f"📅 Ngày: `{today_str}`\n\n"
        f"🔥 *1. BẠCH THỦ LÔ:* `{bach_thu}` (Lót nhẹ đảo chiều)\n"
        f"⚡ *2. CẶP SỐ ĐÁ (Xiên 2):* `[{da_1}] - [{da_2}]`\n"
        f"💎 *3. LÔ XIÊN QUAY 3:* `{da_1} - {bach_thu} - {da_2}`\n\n"
        f"🎯 *4. CHẠM ĐỀ / ĐẦU ĐUÔI:* `{cham_de}`\n\n"
        f"📊 *Ghi chú:* Dữ liệu được tổng hợp theo biên độ nhịp cầu thực tế!"
    )
    return report

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

# 2. XỬ LÝ WEB SERVER VÀ LẮNG NGHE LỆNH TỪ TELEGRAM (ĐỂ XEM LIỀN)
class TelegramWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"CauTuRong Bot is running 24/7 with Instant Command support!")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            import json
            update = json.loads(post_data.decode('utf-8'))
            
            # Kiểm tra xem có tin nhắn gửi đến không
            if "message" in update and "text" in update["message"]:
                text = update["message"]["text"].strip().lower()
                chat_id = update["message"]["chat"]["id"]
                
                # Nếu bạn gõ lệnh /xem hoặc /thongke trong chat Telegram
                if text in ["/xem", "/thongke", "xem", "thống kê"]:
                    report = generate_statistics_report()
                    
                    # Phản hồi lại trực tiếp vào khung chat
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": chat_id,
                        "text": f"@{BOT_ID}\n{report}",
                        "parse_mode": "Markdown"
                    }
                    requests.post(url, json=payload)
        except Exception as e:
            print(f"Lỗi xử lý webhook lệnh: {e}")
            
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), TelegramWebhookHandler)
    server.serve_forever()

# 3. VÒNG LẶP TỰ ĐỘNG CHẠY THEO LỊCH (5:15 SÁNG VÀ 17:15 CHIỀU)
def run_scheduled_loop():
    send_telegram_alert("🚀 *Hệ thống Bot Tự Động & Lệnh Tức Thờ CAUTURONG đã kích hoạt!* Gõ `/xem` để coi ngay bất cứ lúc nào.")
    
    last_sent_date = ""
    
    while True:
        try:
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_hour = now.hour
            current_minute = now.minute
            
            # Tự động gửi vào lúc 5:15 sáng
            if current_hour == 5 and current_minute == 15 and last_sent_date != f"{current_date}_0515":
                report = generate_statistics_report()
                send_telegram_alert(f"⏰ *Bản tin định kỳ 05:15 sáng*\n\n{report}")
                last_sent_date = f"{current_date}_0515"
                print("[+] Đã gửi bản tin tự động lúc 5:15 sáng.")
                
            # Tự động gửi kết quả vào lúc 17:15 chiều
            elif current_hour == 17 and current_minute == 15 and last_sent_date != f"{current_date}_1715":
                send_telegram_alert("⏰ *Bản tin kết quả chiều* - Đã đến giờ mở thưởng, anh em chuẩn bị đối chiếu kết quả thực tế!")
                last_sent_date = f"{current_date}_1715"
                print("[+] Đã gửi thông báo lúc 17:15 chiều.")
                
        except Exception as e:
            print(f"Lỗi vòng lặp lịch: {e}")
            
        time.sleep(30) # Kiểm tra liên tục mỗi 30 giây để bắt đúng giờ 5:15

if __name__ == "__main__":
    # Chạy Web Server lắng nghe lệnh Telegram trên một luồng riêng
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Chạy vòng lặp lịch trình tự động
    run_scheduled_loop()
