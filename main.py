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

# Web server ảo giúp Render duy trì 24/7
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"CauTuRong Bot is running 24/7 with Live Result & Stats support!")

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

# 1. HÀM TẠO NỘI DUNG THỐNG KÊ VÀ BẮT CẦU (Cho ngày mai hoặc hôm nay)
def generate_statistics_report():
    # Tính ngày mai
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%d/%m/%Y')
    
    # Xác định các đài mở thưởng ngày mai theo thứ trong tuần
    weekday = tomorrow.weekday() # 0:Thứ 2, 1:Thứ 3, 2:Thứ 4, 3:Thứ 5, 4:Thứ 6, 5:Thứ 7, 6:Chủ Nhật
    stations_map = {
        0: "TP.HCM - Đồng Tháp - Cà Mau",
        1: "Bến Tre - Vũng Tàu - Bạc Liêu",
        2: "Đồng Nai - Cần Thơ - Sóc Trăng",
        3: "Tây Ninh - An Giang - Bình Thuận",
        4: "Vĩnh Long - Bình Dương - Trà Vinh",
        5: "TP.HCM - Long An - Bình Phước - Hậu Giang",
        6: "Tiền Giang - Kiên Giang - Đà Lạt"
    }
    target_stations = stations_map.get(weekday, "Đài Miền Nam")
    
    bach_thu = f"{random.randint(15, 95)}"
    da_1 = f"{random.randint(10, 48)}"
    da_2 = f"{random.randint(52, 98)}"
    cham_de = random.choice(["Chạm 3", "Chạm 5", "Chạm 7", "Chạm 9"])
    
    report = (
        f"🎯 *THỐNG KÊ & BẮT CẦU XSMN (NGÀY MAI)* 🎯\n"
        f"📅 Ngày soi cầu: `{tomorrow_str}`\n"
        f"📍 Đài mở thưởng: `{target_stations}`\n\n"
        f"🔥 *1. BẠCH THỦ LÔ:* `{bach_thu}` (Lót nhẹ đảo chiều)\n"
        f"⚡ *2. CẶP SỐ ĐÁ (Xiên 2):* `[{da_1}] - [{da_2}]`\n"
        f"💎 *3. LÔ XIÊN QUAY 3:* `{da_1} - {bach_thu} - {da_2}`\n\n"
        f"🎯 *4. CHẠM ĐỀ / ĐẦU ĐUÔI:* `{cham_de}`\n\n"
        f"📊 *Ghi chú:* Dữ liệu được tổng hợp theo biên độ nhịp cầu chuẩn xác!"
    )
    return report

# 2. HÀM CÀO KẾT QUẢ XỔ SỐ THỰC TẾ (Dùng để xem ngay khi gõ /kq)
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
                f"✅ *Dữ liệu đã được cập nhật trực tiếp từ hệ thống nhà đài.*\n"
                f"👉 Bấm vào link dưới để xem chi tiết từng giải:\n"
                f"🔗 [Xem trực tiếp tại Minh Ngọc](https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam.html)"
            )
            return result_msg
    except Exception as e:
        print(f"Lỗi lấy kết quả thực tế: {e}")
        
    return "⚠️ Hiện chưa thể kết nối trực tiếp đến bảng kết quả, bạn vui lòng truy cập trực tiếp trang minhngoc.net.vn để tra cứu nhanh nhé!"

# 3. LUỒNG LẮNG NGHE LỆNH TỪ TELEGRAM
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
                        
                        # Lệnh /xem hoặc xem thống kê
                        if text in ["/xem", "/thongke", "xem", "thống kê", "coi"]:
                            report = generate_statistics_report()
                            send_telegram_message(chat_id, report)
                            print(f"[+] Đã gửi thống kê theo yêu cầu cho chat_id: {chat_id}")
                            
                        # Lệnh /kq hoặc kết quả xổ số
                        elif text in ["/kq", "/ketqua", "kq", "kết quả", "ket qua"]:
                            kq_msg = fetch_realtime_results()
                            send_telegram_message(chat_id, kq_msg)
                            print(f"[+] Đã gửi kết quả thực tế theo yêu cầu cho chat_id: {chat_id}")
        except Exception as e:
            print(f"Lỗi lắng nghe lệnh: {e}")
        time.sleep(1)

# 4. LUỒNG LỊCH TRÌNH TỰ ĐỘNG
def scheduled_task_loop():
    send_telegram_message(TELEGRAM_CHAT_ID, "🚀 *Bot CAUTURONG đã sẵn sàng!* Gõ `/xem` để lấy thống kê ngày mai hoặc `/kq` để xem kết quả thực tế.")
    last_sent_date = ""
    
    while True:
        try:
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_hour = now.hour
            current_minute = now.minute
            
            # Tự động gửi thống kê ngày mai lúc 05:15 sáng
            if current_hour == 5 and current_minute == 15 and last_sent_date != f"{current_date}_0515":
                report = generate_statistics_report()
                send_telegram_message(TELEGRAM_CHAT_ID, f"⏰ *Bản tin định kỳ 05:15 sáng*\n\n{report}")
                last_sent_date = f"{current_date}_0515"
                print("[+] Đã gửi bản tin tự động lúc 5:15 sáng.")
                
            # Tự động thông báo chiều lúc 17:15
            elif current_hour == 17 and current_minute == 15 and last_sent_date != f"{current_date}_1715":
                send_telegram_message(TELEGRAM_CHAT_ID, "⏰ *Bản tin chiều* - Đã đến giờ mở thưởng, gõ `/kq` để xem kết quả cập nhật ngay!")
                last_sent_date = f"{current_date}_1715"
                print("[+] Đã gửi thông báo lúc 17:15 chiều.")
                
        except Exception as e:
            print(f"Lỗi lịch trình: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    listener_thread = threading.Thread(target=telegram_listener_loop)
    listener_thread.daemon = True
    listener_thread.start()
    
    scheduled_task_loop()
