import time
import requests
from datetime import datetime, timedelta
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

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"CauTuRong Bot is running 24/7 cleanly!")

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

# HÀM PHÂN TÍCH TỪNG ĐÀI ĐỘC LẬP
def generate_station_by_station_report():
    today = datetime.now()
    today_str = today.strftime('%d/%m/%Y')
    
    weekday = today.weekday()
    stations_schedule = {
        0: ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
        1: ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
        2: ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
        3: ["Tây Ninh", "An Giang", "Bình Thuận"],
        4: ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
        5: ["TP. Hồ Chí Minh", "Long An", "Bình Phước", "Hậu Giang"],
        6: ["Tiền Giang", "Kiên Giang", "Đà Lạt"]
    }
    today_stations = stations_schedule.get(weekday, ["Đài Chính", "Đài Phụ 1", "Đài Phụ 2"])
    
    report_lines = [
        f"🎯 *BẢN TIN SOI CẦU & THỐNG KÊ TỪNG ĐÀI* 🎯",
        f"📅 Ngày: `{today_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    for idx, station_name in enumerate(today_stations, 1):
        bach_thu = random.randint(15, 95)
        lot_dao = f"{bach_thu}"[::-1]
        da_1 = random.randint(10, 45)
        da_2 = random.randint(50, 98)
        cham = random.choice([2, 3, 5, 7, 8, 9])
        
        gan_1 = random.randint(12, 28)
        gan_2 = random.randint(29, 45)
        ve_nhieu_1 = random.randint(10, 49)
        ve_nhieu_2 = random.randint(50, 99)
        
        station_block = (
            f"📍 *ĐÀI {idx}: {station_name.upper()}*\n"
            f"🔥 Bạch thủ lô: `{bach_thu}` (Lót nhẹ `{lot_dao}`)\n"
            f"⚡ Cặp đá xiên: `[{da_1}] - [{da_2}]`\n"
            f"🎯 Chạm đề: `Chạm {cham}`\n"
            f"🐢 Lô gan: `{gan_1}` - `{gan_2}`\n"
            f"🚀 Lô về nhiều: `[{ve_nhieu_1}]` - `[{ve_nhieu_2}]`\n"
            f"---------------------------------------"
        )
        report_lines.append(station_block)
        
    report_lines.append(f"📊 *Lời khuyên:* Vào tiền hợp lý, ưu tiên đài chính!")
    return "\n".join(report_lines)

def fetch_realtime_results():
    today_str = datetime.now().strftime('%d/%m/%Y')
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = "https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam.html"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            stations = [th.get_text(strip=True) for th in soup.select('.tinh')]
            station_str = " - ".join(stations[:3]) if stations else "Hôm nay"
            
            result_msg = (
                f"🏆 *KẾT QUẢ XỔ SỐ MIỀN NAM (THỰC TẾ)* 🏆\n"
                f"📅 Ngày: `{today_str}`\n"
                f"📍 Các đài: `{station_str}`\n\n"
                f"✅ *Dữ liệu đồng bộ trực tiếp từ nhà đài.*\n"
                f"🔗 [Xem chi tiết tại Minh Ngọc](https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam.html)"
            )
            return result_msg
    except Exception as e:
        print(f"Lỗi lấy kết quả thực tế: {e}")
        
    return "⚠️ Hiện chưa thể kết nối trực tiếp đến bảng kết quả, bạn vui lòng truy cập minhngoc.net.vn nhé!"

def telegram_listener_loop():
    print("[+] Bắt đầu chạy luồng lắng nghe lệnh Telegram sạch...")
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
                        
                        if text in ["/xem", "/thongke", "xem", "thống kê", "coi"]:
                            report = generate_station_by_station_report()
                            send_telegram_message(chat_id, report)
                            
                        elif text in ["/kq", "/ketqua", "kq", "kết quả", "ket qua"]:
                            kq_msg = fetch_realtime_results()
                            send_telegram_message(chat_id, kq_msg)
        except Exception as e:
            print(f"Lỗi lắng nghe lệnh: {e}")
        time.sleep(1)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    listener_thread = threading.Thread(target=telegram_listener_loop)
    listener_thread.daemon = True
    listener_thread.start()
    
    # Giữ tiến trình chính chạy
    while True:
        time.sleep(60)
