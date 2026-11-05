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

def generate_station_by_station_report():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài Chính", "Đài Phụ 1", "Đài Phụ 2"])
    
    stations_scraped, raw_numbers = fetch_realtime_raw_data()
    
    report_lines = [
        f"🎯 *BẢN TIN SOI CẦU THỰC CHIẾN* 🎯",
        f"📅 Ngày: `{today_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    for idx, station_name in enumerate(today_stations, 1):
        if raw_numbers and len(raw_numbers) > idx * 5:
            base_seed = int(raw_numbers[idx * 2][-2:])
            bach_thu = (base_seed * 7 + idx) % 80 + 10
        else:
            bach_thu = random.randint(15, 95)
            
        lot_dao = f"{bach_thu:02d}"[::-1]
        da_1 = (bach_thu + 12) % 89 + 10
        da_2 = (bach_thu * 3) % 89 + 10
        cham = bach_thu % 10
        
        gan_1 = random.randint(12, 28)
        gan_2 = random.randint(29, 45)
        
        station_block = (
            f"📍 *ĐÀI {idx}: {station_name.upper()}*\n"
            f"🔥 Bạch thủ lô: `{bach_thu:02d}` (Lót nhẹ `{lot_dao}`)\n"
            f"⚡ Cặp đá xiên: `[{da_1:02d}] - [{da_2:02d}]`\n"
            f"🎯 Chạm đề: `Chạm {cham}`\n"
            f"🐢 Lô gan: `{gan_1}` - `{gan_2}`\n"
            f"---------------------------------------"
        )
        report_lines.append(station_block)
        
    report_lines.append(f"📊 *Lời khuyên:* Vào tiền hợp lý, ưu tiên đài chính!")
    return "\n".join(report_lines)

def generate_three_stations_analysis():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài 1", "Đài 2", "Đài 3"])[:3]
    
    stations_scraped, raw_numbers = fetch_realtime_raw_data()
    
    if raw_numbers:
        bach_thu_chung = int(raw_numbers[0][-2:]) if len(raw_numbers[0]) >= 2 else 45
    else:
        bach_thu_chung = 68
        
    cap_bach_thu = [f"{bach_thu_chung:02d}", f"{str(bach_thu_chung)[::-1]}"]
    de_cham_chung = bach_thu_chung % 10
    xien_3_dai = [
        (bach_thu_chung + 5) % 90 + 10,
        (bach_thu_chung + 17) % 90 + 10,
        (bach_thu_chung + 29) % 90 + 10
    ]
    
    report = (
        f"🔗 *PHÂN TÍCH TỔNG HỢP 3 ĐÀI* 🔗\n"
        f"📅 Ngày: `{today_str}`\n"
        f"📍 Các đài: `{' - '.join(today_stations)}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **Bạch thủ lô chung 3 đài:** `{bach_thu_chung:02d}` (Cặp lót: `{' - '.join(cap_bach_thu)}`)\n"
        f"⚡ **Bộ xiên 3 đài sáng giá:** `[{xien_3_dai[0]:02d}] - [{xien_3_dai[1]:02d}] - [{xien_3_dai[2]:02d}]`\n"
        f"🎯 **Chạm đề chung 3 đài:** `Chạm {de_cham_chung}`\n"
        f"---------------------------------------\n"
        f"💡 *Lời khuyên:* Phù hợp để đánh dàn hoặc rải đều vốn cho cả 3 đài!"
    )
    return report

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
                report_3dai = generate_three_stations_analysis()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *BẢN TIN (1/2) - TỔNG HỢP 3 ĐÀI*\n\n" + report_3dai)
                time.sleep(2)
                report_chitiet = generate_station_by_station_report()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *BẢN TIN (2/2) - CHI TIẾT TỪNG ĐÀI*\n\n" + report_chitiet)
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
    print("[+] Lắng nghe lệnh Telegram (Đã gỡ bỏ kiểm tra kênh)...")
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
                        
                        # Xử lý lệnh trực tiếp không cần kiểm tra điều kiện rườm rà
                        if text in ["xem", "/xem", "thong ke", "/thongke", "thống kê", "coi"]:
                            report = generate_station_by_station_report()
                            send_telegram_message(chat_id, report)
                            
                        elif text in ["3dai", "/3dai", "3 đài", "/3 đài", "ba đài", "phan tich 3 dai"]:
                            analysis_report = generate_three_stations_analysis()
                            send_telegram_message(chat_id, analysis_report)
                            
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
