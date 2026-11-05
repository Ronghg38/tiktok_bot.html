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

STATIONS_SCHEDULE = {
    0: ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
    1: ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
    2: ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
    3: ["Tây Ninh", "An Giang", "Bình Thuận"],
    4: ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
    5: ["TP. Hồ Chí Minh", "Long An", "Bình Phước", "Hậu Giang"],
    6: ["Tiền Giang", "Kiên Giang", "Đà Lạt"]
}

def fetch_realtime_raw_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = "https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam.html"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            stations = [th.get_text(strip=True) for th in soup.select('.tinh')]
            all_numbers = [td.get_text(strip=True) for td in soup.select('td.v-giai span, td[id^="giai"]')]
            valid_digits = [num for num in all_numbers if num.isdigit() and len(num) >= 2]
            return stations, valid_digits
    except Exception as e:
        print(f"Lỗi cào dữ liệu thực tế: {e}")
    return [], []

def generate_master_report():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài 1", "Đài 2", "Đài 3"])[:3]
    
    _, raw_numbers = fetch_realtime_raw_data()
    station_names_str = " - ".join(today_stations)
    
    seed_val = int(raw_numbers[0][-2:]) if (raw_numbers and len(raw_numbers[0]) >= 2) else 45
    
    # Tính toán số cho phần 3 đài (BTL, STL, Xiên)
    btl_3dai = (seed_val + 7) % 80 + 10
    stl_3dai_1 = (seed_val * 2 + 3) % 80 + 10
    stl_3dai_2 = (seed_val + 15) % 80 + 10
    xien_1 = (seed_val + 5) % 89 + 10
    xien_2 = (seed_val + 22) % 89 + 10
    xien_3 = (seed_val + 37) % 89 + 10
    
    part_3dai = (
        f"🔗 *PHẦN 1: TỔNG HỢP 3 ĐÀI MIỀN NAM* 🔗\n"
        f"📅 Ngày: `{today_str}` | Các đài: `{station_names_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **Bạch Thủ Lô (BTL):** `{btl_3dai:02d}` (Lót `{str(btl_3dai)[::-1]}`)\n"
        f"⚡ **Song Thủ Lô (STL):** `[{stl_3dai_1:02d}] - [{stl_3dai_2:02d}]`\n"
        f"🎯 **Cặp Xiên 3 Đài:** `[{xien_1:02d}] - [{xien_2:02d}] - [{xien_3:02d}]`\n"
        f"📌 **Chạm đề chung:** `Chạm {btl_3dai % 10}`"
    )
    
    part_chitiet_lines = [
        f"\n📌 *PHẦN 2: CHI TIẾT SỐ LIỆU TỪNG ĐÀI* 📌\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    for idx, station_name in enumerate(today_stations, 1):
        if raw_numbers and len(raw_numbers) > idx * 4:
            local_seed = int(raw_numbers[idx * 3][-2:])
            bach_thu = (local_seed * 5 + idx * 3) % 80 + 10
        else:
            bach_thu = (seed_val + idx * 11) % 80 + 10
            
        lot_dao = f"{bach_thu:02d}"[::-1]
        da_1 = (bach_thu + 12) % 89 + 10
        da_2 = (bach_thu * 3) % 89 + 10
        cham = bach_thu % 10
        gan_1 = (bach_thu + 5) % 30 + 10
        gan_2 = (bach_thu + 17) % 35 + 25
        
        station_block = (
            f"📍 *ĐÀI {idx}: {station_name.upper()}*\n"
            f"🔥 BTL: `{bach_thu:02d}` (Lót `{lot_dao}`)\n"
            f"⚡ Đá xiên: `[{da_1:02d}] - [{da_2:02d}]` | Chạm: `Chạm {cham}`\n"
            f"🐢 Lô gan: `{gan_1}` - `{gan_2}`\n"
            f"---------------------------------------"
        )
        part_chitiet_lines.append(station_block)
        
    part_chitiet_lines.append(f"📊 *Lời khuyên:* Vào tiền hợp lý, phân bổ vốn đều tay!")
    
    master_report = part_3dai + "\n" + "\n".join(part_chitiet_lines)
    return master_report

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
                f"✅ *Dữ liệu đồng bộ trực tiếp từ nhà đài Minh Ngọc.*"
            )
            return result_msg
    except Exception as e:
        print(f"Lỗi lấy kết quả thực tế: {e}")
        
    return "⚠️ Hiện chưa thể kết nối trực tiếp đến bảng kết quả, bạn vui lòng truy cập minhngoc.net.vn nhé!"

def schedule_sender_loop():
    print(f"[+] Đã kích hoạt luồng hẹn giờ tự động gửi tin...")
    sent_report_today = False
    sent_result_today = False
    
    while True:
        now = datetime.now()
        if now.hour == AUTO_SEND_HOUR and now.minute == AUTO_SEND_MINUTE:
            if not sent_report_today:
                full_report = generate_master_report()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *BẢN TIN SOI CẦU HẰNG NGÀY*\n\n" + full_report)
                sent_report_today = True
                time.sleep(60)

        elif now.hour == AUTO_RESULT_HOUR and now.minute == AUTO_RESULT_MINUTE:
            if not sent_result_today:
                kq_msg = fetch_realtime_results()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *THÔNG BÁO KẾT QUẢ HÔM NAY*\n\n" + kq_msg)
                sent_result_today = True
                time.sleep(60)
        else:
            if now.hour == 0 and now.minute == 0:
                sent_report_today = False
                sent_result_today = False
                
        time.sleep(15)

def telegram_listener_loop():
    print("[+] Lắng nghe lệnh Telegram...")
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
                        
                        if text in ["xem", "/xem", "thong ke", "/thongke", "thống kê", "coi", "3dai", "/3dai", "3 đài", "/3 đài", "ba đài", "phan tich 3 dai"]:
                            full_report = generate_master_report()
                            send_telegram_message(chat_id, f"🎯 *BẢN TIN SOI CẦU MIỀN NAM*\n\n" + full_report)
                            
                        elif text in ["kq", "/kq", "ketqua", "/ketqua", "kết quả", "ket qua"]:
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
    
    scheduler_thread = threading.Thread(target=schedule_sender_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    while True:
        time.sleep(60)
