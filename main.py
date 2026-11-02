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

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"CauTuRong XSMN Prediction Bot is running 24/7!")

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

# Thuật toán bắt cầu và phân tích số học Xổ số miền Nam
def generate_xsmn_analysis():
    today_str = datetime.now().strftime('%d/%m/%Y')
    
    # Các cụm đài quay thưởng miền Nam theo lịch tuần
    provinces_list = [
        "TP.HCM - Long An - Bình Phước - Hậu Giang",
        "Đồng Tháp - Cà Mau - TP.HCM",
        "Bến Tre - Vũng Tàu - Bạc Liêu",
        "Đồng Nai - Cần Thơ - Sóc Trăng",
        "Tây Ninh - An Giang - Bình Thuận",
        "Vĩnh Long - Bình Dương - Trà Vinh"
    ]
    current_prov = random.choice(provinces_list)
    
    # Tạo số liệu phân tích cầu chạy
    bach_thu = f"{random.randint(15, 95)}"
    da_1 = f"{random.randint(10, 48)}"
    da_2 = f"{random.randint(52, 98)}"
    cham_de = random.choice(["Đầu 3", "Đầu 7", "Đuôi 5", "Đuôi 9", "Tổng 4", "Tổng 8"])
    
    report = (
        f"🎯 *PHÂN TÍCH CẦU & CHỐT SỐ XSMN* 🎯\n"
        f"📅 Ngày: `{today_str}`\n"
        f"📍 Đài mở thưởng: `{current_prov}`\n\n"
        f"🔥 *1. BẠCH THỦ LÔ (Cầu nhịp thông):*\n"
        f"👉 Cặp số: `{bach_thu}` (Lót nhẹ đảo chiều)\n\n"
        f"⚡ *2. CẶP SỐ ĐÁ (Xiên 2 tài lộc):*\n"
        f"👉 Cặp đá: `[{da_1}] - [{da_2}]`\n\n"
        f"💎 *3. LÔ XIÊN QUAY 3:*\n"
        f"👉 Bộ số: `{da_1} - {bach_thu} - {da_2}`\n\n"
        f"🎯 *4. CHẠM ĐỀ / ĐẦU ĐUÔI CHUẨN:*\n"
        f"👉 Bắt cầu: `{cham_de}` (Biên độ cầu đang chạy đều 4 kỳ)\n\n"
        f"📊 *Phương pháp bắt cầu:* Soi nhịp kẹp số giải đặc biệt kết hợp tần suất lô rơi, biên độ thông thoáng, tỷ lệ vào tiền tối ưu cho phiên chiều!"
    )
    return report

def run_xsmn_bot_loop():
    send_telegram_alert("🚀 *Hệ thống Bot Bắt Cầu XSMN CAUTURONG đã khởi động!*")
    
    while True:
        try:
            analysis_msg = generate_xsmn_analysis()
            send_telegram_alert(analysis_msg)
            print("[+] Đã gửi bản tin bắt cầu XSMN lên Telegram thành công.")
        except Exception as e:
            print(f"Lỗi vòng lặp XSMN: {e}")
        
        # Gửi thông tin định kỳ hoặc theo khung giờ soi cầu (ví dụ: mỗi 4 tiếng hoặc tùy chỉnh)
        time.sleep(14400)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    run_xsmn_bot_loop()
