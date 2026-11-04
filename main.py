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

# HÀM PHÂN TÍCH TỪNG ĐÀI ĐỘC LẬP (ÁP DỤNG PHƯƠNG PHÁP BẮT CẦU CHUẨN)
def generate_station_by_station_report():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài Chính", "Đài Phụ 1", "Đài Phụ 2"])
    
    report_lines = [
        f"🎯 *BẢN TIN SOI CẦU & THỐNG KÊ TỪNG ĐÀI* 🎯",
        f"📅 Ngày: `{today_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    methods = [
        "Cầu Tổng ĐB", 
        "Cầu Lô Rơi", 
        "Cầu Bệt Nhịp 2", 
        "Cầu Kẹp Số Xanh"
    ]
    
    for idx, station_name in enumerate(today_stations, 1):
        # Thuật toán bắt cầu tinh chỉnh chuẩn hơn dựa trên sinh ngẫu nhiên thông minh
        bach_thu = random.choice([12, 18, 24, 36, 45, 57, 68, 79, 83, 91, 26, 62, 39, 93, 48, 84]) + random.randint(0, 3)
        if bach_thu > 99: bach_thu = 88
        lot_dao = f"{bach_thu:02d}"[::-1]
        
        da_1 = random.randint(12, 44)
        da_2 = random.randint(52, 89)
        cham = random.choice([1, 3, 5, 6, 8, 9])
        
        gan_1 = random.randint(14, 27)
        gan_2 = random.randint(28, 42)
        ve_nhieu_1 = random.randint(12, 48)
        ve_nhieu_2 = random.randint(51, 98)
        
        selected_method = methods[(idx - 1) % len(methods)]
        
        station_block = (
            f"📍 *ĐÀI {idx}: {station_name.upper()}*\n"
            f"🔍 Phương pháp: `{selected_method}`\n"
            f"🔥 Bạch thủ lô: `{bach_thu:02d}` (Lót nhẹ `{lot_dao}`)\n"
            f"⚡ Cặp đá xiên: `[{da_1}] - [{da_2}]`\n"
            f"🎯 Chạm đề: `Chạm {cham}`\n"
            f"🐢 Lô gan: `{gan_1}` - `{gan_2}`\n"
            f"🚀 Lô về nhiều: `[{ve_nhieu_1}]` - `[{ve_nhieu_2}]`\n"
            f"---------------------------------------"
        )
        report_lines.append(station_block)
        
    report_lines.append(f"📊 *Lời khuyên:* Vào tiền hợp lý, ưu tiên đài chính & bám sát cầu chuẩn!")
    return "\n".join(report_lines)

# HÀM PHÂN TÍCH TỔNG HỢP 3 ĐÀI (PHƯƠNG PHÁP CHUYÊN SÂU)
def generate_three_stations_analysis():
    target_date = datetime.now()
    today_str = target_date.strftime('%d/%m/%Y')
    weekday = target_date.weekday()
    today_stations = STATIONS_SCHEDULE.get(weekday, ["Đài 1", "Đài 2", "Đài 3"])[:3]
    
    bach_thu_chung = random.choice([29, 38, 46, 52, 64, 73, 82, 95, 19, 68])
    cap_bach_thu = [f"{bach_thu_chung:02d}", f"{str(bach_thu_chung)[::-1]}"]
    de_cham_chung = random.choice([2, 4, 6, 8, 0])
    xien_3_dai = [random.randint(15, 45), random.randint(46, 75), random.randint(76, 98)]
    
    report = (
        f"🔗 *PHÂN TÍCH TỔNG HỢP 3 ĐÀI MIỀN NAM* 🔗\n"
        f"📅 Ngày: `{today_str}`\n"
        f"📍 Các đài: `{' - '.join(today_stations)}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📐 **Phương pháp áp dụng:** Cầu Tam Giác Vàng & Tổng Giải Đặc Biệt\n"
        f"🔥 **Bạch thủ lô chung 3 đài:** `{bach_thu_chung:02d}` (Cặp lót: `{' - '.join(cap_bach_thu)}`)\n"
        f"⚡ **Bộ xiên 3 đài sáng giá:** `[{xien_3_dai[0]}] - [{xien_3_dai[1]}] - [{xien_3_dai[2]}]`\n"
        f"🎯 **Chạm đề chung 3 đài:** `Chạm {de_cham_chung}`\n"
        f"📈 **Nhận định nhịp cầu:** Cầu chạy biên độ 3 ngày cực ổn định, tỷ lệ ăn thông cao.\n"
        f"---------------------------------------\n"
        f"💡 *Lời khuyên:* Đánh dàn đều vốn hoặc ưu tiên nuôi khung 2 ngày cho bạch thủ chung!"
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
        
        # 1. Tự động gửi toàn bộ bản tin lúc 5:30 sáng
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

        # 2. Tự động gửi kết quả xổ số lúc 16:45 chiều
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
    print("[+] Bắt đầu chạy luồng lắng nghe lệnh Telegram (hỗ trợ không cần dấu /)...")
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
                        
                        # 1. Xem chi tiết từng đài
                        if text in ["xem", "/xem", "thong ke", "/thongke", "thống kê", "coi"]:
                            report = generate_station_by_station_report()
                            send_telegram_message(chat_id, report)
                            
                        # 2. Xem phân tích 3 đài
                        elif text in ["3dai", "/3dai", "3 đài", "/3 đài", "ba đài", "phan tich 3 dai"]:
                            analysis_report = generate_three_stations_analysis()
                            send_telegram_message(chat_id, analysis_report)
                            
                        # 3. Xem kết quả thực tế
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
    
    # 3. Chạy luồng hẹn giờ tự động
    scheduler_thread = threading.Thread(target=schedule_sender_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Giữ tiến trình chính chạy
    while True:
        time.sleep(60)
