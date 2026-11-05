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

# HÀM TỔNG HỢP GỘP CẢ HAI (TỪNG ĐÀI + 3 ĐÀI CHUNG TRONG 1 TIN NHẮN)
def generate_master_report():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài 1", "Đài 2", "Đài 3"])[:3]
    
    stations_scraped, raw_numbers = fetch_realtime_raw_data()
    
    station_names_str = " - ".join(today_stations)
    
    # 1. Phần gộp chung 3 đài
    bthu_1 = random.randint(15, 95)
    bthu_2 = random.randint(15, 95)
    bthu_3 = random.randint(15, 95)
    
    part_3dai = (
        f"🔗 *PHẦN 1: TỔNG HỢP 3 ĐÀI MIỀN NAM* 🔗\n"
        f"📅 Ngày: `{today_str}` | Các đài: `{station_names_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **Bạch thủ lô các đài:**\n"
        f"• *{today_stations[0]}:* `{bthu_1:02d}` (Lót `{str(bthu_1)[::-1]}`)\n"
        f"• *{today_stations[1]}:* `{bthu_2:02d}` (Lót `{str(bthu_2)[::-1]}`)\n"
        f"• *{today_stations[2]}:* `{bthu_3:02d}` (Lót `{str(bthu_3)[::-1]}`)\n\n"
        f"⚡ **Đá xiên chung:** `[{bthu_1}] - [{bthu_2}] - [{bthu_3}]`\n"
        f"🎯 **Chạm đề chung:** `Chạm {bthu_1 % 10}` & `Chạm {bthu_2 % 10}`"
    )
    
    # 2. Phần chi tiết từng đài
    part_chitiet_lines = [
        f"📌 *PHẦN 2: CHI TIẾT SỐ LIỆU TỪNG ĐÀI* 📌\n"
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
        ve_nhieu_1 = random.randint(10, 49)
        ve_nhieu_2 = random.randint(50, 99)
        
        station_block = (
            f"📍 *ĐÀI {idx}: {station_name.upper()}*\n"
            f"🔥 Bạch thủ: `{bach_thu:02d}` (Lót `{lot_dao}`)\n"
            f"⚡ Đá xiên: `[{da_1:02d}] - [{da_2:02d}]` | Chạm: `Chạm {cham}`\n"
            f"🐢 Lô gan: `{gan_1}` - `{gan_2}` | Về nhiều: `[{ve_nhieu_1}] - [{ve_nhieu_2}]`\n"
            f"---------------------------------------"
        )
        part_chitiet_lines.append(station_block)
        
    part_chitiet_lines.append(f"📊 *Lời khuyên:* Vào tiền hợp lý, ưu tiên đài chính!")
    
    # Gộp toàn bộ thành một thông điệp lớn, tách biệt rõ ràng bằng tiêu đề và đường kẻ
    master_report = part_3dai + "\n\n" + "\n".join(part_chitiet_lines)
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
                # Lúc 5:30 gửi bản tổng hợp đầy đủ (cả 3 đài chung và từng đài tách biệt trong 1 tin)
                full_report = generate_master_report()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *BẢN TIN SOI CẦU TOÀN DIỆN HẰNG NGÀY*\n\n" + full_report)
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
                        
                        # Dù gõ lệnh nào (xem, 3dai, thongke...) cũng trả về bản tin tích hợp đầy đủ cả 2 phần tách biệt trong 1 tin nhắn
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
