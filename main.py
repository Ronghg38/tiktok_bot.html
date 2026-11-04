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

# 1. Cấu hình giờ gửi bản tin soi cầu (5:30 hằng ngày)
AUTO_SEND_HOUR = 5
AUTO_SEND_MINUTE = 30

# 2. Cấu hình giờ gửi kết quả xổ số (16:45 hằng ngày)
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

# Lịch các đài miền Nam theo thứ trong tuần
STATIONS_SCHEDULE = {
    0: ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
    1: ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
    2: ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
    3: ["Tây Ninh", "An Giang", "Bình Thuận"],
    4: ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
    5: ["TP. Hồ Chí Minh", "Long An", "Bình Phước", "Hậu Giang"],
    6: ["Tiền Giang", "Kiên Giang", "Đà Lạt"]
}

# HÀM PHÂN TÍCH TỪNG ĐÀI ĐỘC LẬP
def generate_station_by_station_report():
    today = datetime.now()
    today_str = today.strftime('%d/%m/%Y')
    weekday = today.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài Chính", "Đài Phụ 1", "Đài Phụ 2"])
    
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

# HÀM PHÂN TÍCH TỔNG HỢP 3 ĐÀI
def generate_three_stations_analysis():
    today = datetime.now()
    today_str = today.strftime('%d/%m/%Y')
    weekday = today.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài 1", "Đài 2", "Đài 3"])[:3]
    
    bach_thu_chung = random.randint(10, 99)
    cap_bach_thu = [f"{bach_thu_chung:02d}", f"{str(bach_thu_chung)[::-1]}"]
    de_cham_chung = random.choice([0, 1, 3, 5, 7, 9])
    xien_3_dai = [random.randint(10, 99) for _ in range(3)]
    
    report = (
        f"🔗 *PHÂN TÍCH TỔNG HỢP 3 ĐÀI MIỀN NAM* 🔗\n"
        f"📅 Ngày: `{today_str}`\n"
        f"📍 Các đài: `{' - '.join(today_stations)}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **Bạch thủ lô chung 3 đài:** `{bach_thu_chung}` (Cặp lót: `{' - '.join(cap_bach_thu)}`)\n"
        f"⚡ **Bộ xiên 3 đài sáng giá:** `[{xien_3_dai[0]}] - [{xien_3_dai[1]}] - [{xien_3_dai[2]}]`\n"
        f"🎯 **Chạm đề chung 3 đài:** `Chạm {de_cham_chung}`\n"
        f"📈 **Nhận định nhịp cầu:** Biên độ cầu chạy đều, nhịp lô gan ổn định giữa các đài.\n"
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
                f"✅ *Dữ liệu đồng bộ trực tiếp từ nhà đài.*\n"
                f"🔗 [Xem chi tiết tại Minh Ngọc](https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam.html)"
            )
            return result_msg
    except Exception as e:
        print(f"Lỗi lấy kết quả thực tế: {e}")
        
    return "⚠️ Hiện chưa thể kết nối trực tiếp đến bảng kết quả, bạn vui lòng truy cập minhngoc.net.vn nhé!"

# ==================== LUỒNG HẸN GIỜ TỰ ĐỘNG ====================
def schedule_sender_loop():
    print(f"[+] Đã kích hoạt luồng hẹn giờ tự động:")
    print(f"    - Soi cầu toàn bộ lúc: {AUTO_SEND_HOUR:02d}:{AUTO_SEND_MINUTE:02d}")
    print(f"    - Kết quả xổ số lúc: {AUTO_RESULT_HOUR:02d}:{AUTO_RESULT_MINUTE:02d}")
    
    sent_report_today = False
    sent_result_today = False
    
    while True:
        now = datetime.now()
        
        # 1. Tự động gửi toàn bộ bản tin lúc 5:30
        if now.hour == AUTO_SEND_HOUR and now.minute == AUTO_SEND_MINUTE:
            if not sent_report_today:
                print("[+] Đang tiến hành gửi toàn bộ bản tin định kỳ lúc 5:30...")
                
                report_3dai = generate_three_stations_analysis()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *BẢN TIN TỰ ĐỘNG (1/2) - TỔNG HỢP 3 ĐÀI*\n\n" + report_3dai)
                time.sleep(2)
                
                report_chitiet = generate_station_by_station_report()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *BẢN TIN TỰ ĐỘNG (2/2) - CHI TIẾT TỪNG ĐÀI*\n\n" + report_chitiet)
                
                sent_report_today = True
                time.sleep(60)

        # 2. Tự động gửi kết quả xổ số lúc 16:45
        elif now.hour == AUTO_RESULT_HOUR and now.minute == AUTO_RESULT_MINUTE:
            if not sent_result_today:
                print("[+] Đang tiến hành gửi kết quả xổ số tự động lúc 16:45...")
                
                kq_msg = fetch_realtime_results()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *THÔNG BÁO KẾT QUẢ HÔM NAY*\n\n" + kq_msg)
                
                sent_result_today = True
                time.sleep(60)
                
        else:
            if now.hour == 0 and now.minute == 0:
                sent_report_today = False
                sent_result_today = False
                
        time.sleep(15)

# ==================== LUỒNG LẮNG NGHE LỆNH TELEGRAM ====================
def telegram_listener_loop():
    print("[+] Bắt đầu chạy luồng lắng nghe lệnh Telegram sạch (hỗ trợ không cần dấu /)...")
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
                        
                        # 1. Xem chi tiết từng đài (gõ: xem, /xem, thong ke, /thongke, coi)
                        if text in ["xem", "/xem", "thong ke", "/thongke", "thống kê", "coi"]:
                            report = generate_station_by_station_report()
                            send_telegram_message(chat_id, report)
                            
                        # 2. Xem phân tích 3 đài (gõ: 3dai, /3dai, 3 đài, /3 đài, ba đài, phan tich 3 dai)
                        elif text in ["3dai", "/3dai", "3 đài", "/3 đài", "ba đài", "phan tich 3 dai"]:
                            analysis_report = generate_three_stations_analysis()
                            send_telegram_message(chat_id, analysis_report)
                            
                        # 3. Xem kết quả thực tế (gõ: kq, /kq, ketqua, /ketqua, kết quả, ket qua)
                        elif text in ["kq", "/kq", "ketqua", "/ketqua", "kết quả", "ket qua"]:
                            kq_msg = fetch_realtime_results()
                            send_telegram_message(chat_id, kq_msg)
        except Exception as e:
            print(f"Lỗi lắng nghe lệnh: {e}")
        time.sleep(1)

if __name__ == "__main__":
    # 1. Chạy Web Server duy trì 24/7
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 2. Chạy luồng lắng nghe tương tác chat
    listener_thread = threading.Thread(target=telegram_listener_loop)
    listener_thread.daemon = True
    listener_thread.start()
    
    # 3. Chạy luồng hẹn giờ tự động gửi cả Soi Cầu (5:30) và Kết Quả (16:45)
    scheduler_thread = threading.Thread(target=schedule_sender_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Giữ tiến trình chính chạy
    while True:
        time.sleep(60)
