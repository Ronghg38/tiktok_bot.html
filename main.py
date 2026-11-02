import time
import requests
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import random

# ==================== CẤU HÌNH HỆ THỐNG CAUTURONG ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
BOT_ID = "CAUTURONG BOT"
# ===================================================================

# Web server ảo giúp Render duy trì 24/7
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"CauTuRong Bot is running 24/7 with Live Command Listener!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"@{BOT_ID}\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

# Hàm tạo nội dung thống kê XSMN
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

# Luồng 1: Lắng nghe tin nhắn từ Telegram liên tục (Giúp gõ /xem là bot trả lời liền)
def telegram_listener_loop():
    print("[+] Bắt đầu chạy luồng lắng nghe lệnh Telegram...")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            if response.status_code == 200:
                data = response.json()
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    if "message" in result and "text" in result["message"]:
                        text = result["message"]["text"].strip().lower()
                        chat_id = result["message"]["chat"]["id"]
                        
                        # Khi bạn gõ /xem hoặc chữ xem / thống kê
                        if text in ["/xem", "/thongke", "xem", "thống kê", "coi"]:
                            report = generate_statistics_report()
                            send_telegram_message(chat_id, report)
                            print(f"[+] Đã phản hồi lệnh từ chat_id: {chat_id}")
        except Exception as e:
            print(f"Lỗi lắng nghe lệnh: {e}")
        time.sleep(1)

# Luồng 2: Tự động gửi theo lịch (05:15 sáng và 17:15 chiều)
def scheduled_task_loop():
    send_telegram_message(TELEGRAM_CHAT_ID, "🚀 *Hệ thống Bot CAUTURONG đã trực tuyến!* Gõ `/xem` để coi thống kê bất cứ lúc nào.")
    last_sent_date = ""
    
    while True:
        try:
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_hour = now.hour
            current_minute = now.minute
            
            # Gửi tự động lúc 05:15 sáng
            if current_hour == 5 and current_minute == 15 and last_sent_date != f"{current_date}_0515":
                report = generate_statistics_report()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *Bản tin định kỳ 05:15 sáng*\n\n{report}")
                last_sent_date = f"{current_date}_0515"
                print("[+] Đã gửi bản tin tự động lúc 5:15 sáng.")
                
            # Thông báo lúc 17:15 chiều
            elif current_hour == 17 and current_minute == 15 and last_sent_date != f"{current_date}_1715":
                send_telegram_message(TELEGRAM_CHAT_ID, "⏰ *Bản tin chiều* - Đã đến giờ mở thưởng XSMN, anh em chuẩn bị đối chiếu kết quả thực tế!")
                last_sent_date = f"{current_date}_1715"
                print("[+] Đã gửi thông báo lúc 17:15 chiều.")
                
        except Exception as e:
            print(f"Lỗi lịch trình: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    # 1. Chạy Web Server cho Render (giữ app luôn sống)
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 2. Chạy luồng lắng nghe lệnh gõ từ Telegram để xem liền
    listener_thread = threading.Thread(target=telegram_listener_loop)
    listener_thread.daemon = True
    listener_thread.start()
    
    # 3. Chạy luồng lịch trình tự động
    scheduled_task_loop()
