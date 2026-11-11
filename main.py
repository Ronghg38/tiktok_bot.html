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

AUTO_SEND_HOUR = 5
AUTO_SEND_MINUTE = 30
AUTO_RESULT_HOUR = 16
AUTO_RESULT_MINUTE = 45
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

STATIONS_MN = {
    0: ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
    1: ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
    2: ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
    3: ["Tây Ninh", "An Giang", "Bình Thuận"],
    4: ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
    5: ["TP. Hồ Chí Minh", "Long An", "Bình Phước", "Hậu Giang"],
    6: ["Tiền Giang", "Kiên Giang", "Đà Lạt"]
}

STATIONS_MT = {
    0: ["Thừa Thiên Huế", "Phú Yên"],
    1: ["Quảng Nam", "Đắk Lắk"],
    2: ["Đà Nẵng", "Khánh Hòa"],
    3: ["Bình Định", "Quảng Trị", "Quảng Bình"],
    4: ["Quảng Ngãi", "Đắk Nông", "Gia Lai"],
    5: ["Ninh Thuận", "Đà Nẵng", "Đắk Nông"],
    6: ["Khánh Hòa", "Kon Tum", "Thừa Thiên Huế"]
}

def fetch_realtime_raw_data(region="mien-nam"):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/{region}.html"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            stations = [th.get_text(strip=True) for th in soup.select('.tinh')]
            all_numbers = [td.get_text(strip=True) for td in soup.select('td.v-giai span, td[id^="giai"]')]
            valid_digits = [num for num in all_numbers if num.isdigit() and len(num) >= 2]
            return stations, valid_digits
    except Exception as e:
        print(f"Lỗi cào dữ liệu {region}: {e}")
    return [], []

def generate_mn_report():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_MN.get(weekday, ["Đài 1", "Đài 2", "Đài 3"])[:3]
    
    _, raw_numbers = fetch_realtime_raw_data("mien-nam")
    station_names_str = " - ".join(today_stations)
    seed_val = int(raw_numbers[0][-2:]) if (raw_numbers and len(raw_numbers[0]) >= 2) else 45
    
    btl = (seed_val + 7) % 80 + 10
    stl_1 = (seed_val * 2 + 3) % 80 + 10
    stl_2 = (seed_val + 15) % 80 + 10
    x_1 = (seed_val + 5) % 89 + 10
    x_2 = (seed_val + 22) % 89 + 10
    x_3 = (seed_val + 37) % 89 + 10
    
    part_3dai = (
        f"🏆 *SOI CẦU MIỀN NAM (3 ĐÀI)* 🏆\n"
        f"📅 Ngày: `{today_str}` | Các đài: `{station_names_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **BTL:** `{btl:02d}` (Lót `{str(btl)[::-1]}`)\n"
        f"⚡ **STL:** `[{stl_1:02d}] - [{stl_2:02d}]`\n"
        f"🎯 **Cặp Xiên:** `[{x_1:02d}] - [{x_2:02d}] - [{x_3:02d}]`\n"
        f"📌 **Chạm đề:** `Chạm {btl % 10}`"
    )
    
    part_chitiet = [f"\n📌 *CHI TIẾT TỪNG ĐÀI MIỀN NAM*:\n━━━━━━━━━━━━━━━━━━━━━━━"]
    for idx, s_name in enumerate(today_stations, 1):
        bach_thu = (seed_val + idx * 11) % 80 + 10
        part_chitiet.append(f"📍 *{s_name.upper()}* ➔ BTL: `{bach_thu:02d}` | Chạm: `Chạm {bach_thu % 10}`")
        
    return part_3dai + "\n" + "\n".join(part_chitiet)

def generate_mt_report():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_MT.get(weekday, ["Đài Miền Trung 1", "Đài Miền Trung 2"])
    
    _, raw_numbers = fetch_realtime_raw_data("mien-trung")
    station_names_str = " - ".join(today_stations)
    seed_val = int(raw_numbers[0][-2:]) if (raw_numbers and len(raw_numbers[0]) >= 2) else 38
    
    btl = (seed_val + 9) % 80 + 10
    stl_1 = (seed_val * 3 + 1) % 80 + 10
    stl_2 = (seed_val + 12) % 80 + 10
    x_1 = (seed_val + 4) % 89 + 10
    x_2 = (seed_val + 18) % 89 + 10
    
    part_mt = (
        f"🏆 *SOI CẦU MIỀN TRUNG* 🏆\n"
        f"📅 Ngày: `{today_str}` | Các đài: `{station_names_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **BTL:** `{btl:02d}` (Lót `{str(btl)[::-1]}`)\n"
        f"⚡ **STL:** `[{stl_1:02d}] - [{stl_2:02d}]`\n"
        f"🎯 **Cặp Xiên:** `[{x_1:02d}] - [{x_2:02d}]`\n"
        f"📌 **Chạm đề:** `Chạm {btl % 10}`"
    )
    return part_mt

def generate_mb_report():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    
    _, raw_numbers = fetch_realtime_raw_data("mien-bac")
    seed_val = int(raw_numbers[0][-2:]) if (raw_numbers and len(raw_numbers[0]) >= 2) else 79
    
    btl = (seed_val + 3) % 80 + 10
    stl_1 = (seed_val + 11) % 80 + 10
    stl_2 = (seed_val + 24) % 80 + 10
    xiên_2 = (seed_val + 8) % 89 + 10
    xiên_3 = (seed_val + 33) % 89 + 10
    
    part_mb = (
        f"🏆 *SOI CẦU MIỀN BẮC* 🏆\n"
        f"📅 Ngày: `{today_str}` | Đài: `Hà Nội (Miền Bắc)`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **BTL:** `{btl:02d}` (Lót `{str(btl)[::-1]}`)\n"
        f"⚡ **STL:** `[{stl_1:02d}] - [{stl_2:02d}]`\n"
        f"🎯 **Xiên 2 / Xiên 3:** `[{xiên_2:02d}] - [{xiên_3:02d}]`\n"
        f"📌 **Chạm đề:** `Chạm {btl % 10}`"
    )
    return part_mb

def fetch_realtime_results(region_url, title):
    today_str = datetime.now().strftime('%d/%m/%Y')
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/{region_url}.html"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            stations = [th.get_text(strip=True) for th in soup.select('.tinh')]
            station_str = " - ".join(stations[:3]) if stations else "Hôm nay"
            
            result_msg = (
                f"🏆 *KẾT QUẢ {title.upper()} (THỰC TẾ)* 🏆\n"
                f"📅 Ngày: `{today_str}`\n"
                f"📍 Các đài: `{station_str}`\n\n"
                f"✅ *Đồng bộ trực tiếp từ Minh Ngọc.*"
            )
            return result_msg
    except Exception as e:
        print(f"Lỗi lấy kết quả: {e}")
    return f"⚠️ Hiện chưa kết nối được kết quả {title}."

def schedule_sender_loop():
    print(f"[+] Kích hoạt hẹn giờ tự động...")
    sent_report_today = False
    while True:
        now = datetime.now()
        if now.hour == AUTO_SEND_HOUR and now.minute == AUTO_SEND_MINUTE:
            if not sent_report_today:
                full_report = generate_mn_report()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *BẢN TIN SOI CẦU MIỀN NAM*\n\n" + full_report)
                sent_report_today = True
                time.sleep(60)
        else:
            if now.hour == 0 and now.minute == 0:
                sent_report_today = False
        time.sleep(15)

def telegram_listener_loop():
    print("[+] Lắng nghe lệnh Telegram sạch (Không có kiểm tra kênh)...")
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
                        
                        if text in ["xem", "mn", "mien nam", "3dai"]:
                            report = generate_mn_report()
                            send_telegram_message(chat_id, report)
                            
                        elif text in ["mt", "mien trung"]:
                            report = generate_mt_report()
                            send_telegram_message(chat_id, report)
                            
                        elif text in ["mb", "mien bac"]:
                            report = generate_mb_report()
                            send_telegram_message(chat_id, report)
                            
                        elif text in ["kq", "ketqua", "kết quả"]:
                            kq_mn = fetch_realtime_results("mien-nam", "Miền Nam")
                            send_telegram_message(chat_id, kq_mn)
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
    
    scheduler_thread = threading.Thread(target=schedule_sender_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    while True:
        time.sleep(60)
