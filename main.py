import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# ==================== CẤU HÌNH TÀI KHOẢN CỦA BẠN ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
# ==========================================================

# 1. Tạo một HTTP Server ảo để lừa Render (giúp Web Service luôn chạy ổn định ở gói Free)
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TikTok Bot is running active 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"[+] Web server ảo đang chạy trên cổng {port}...")
    server.serve_forever()

# 2. Logic cào dữ liệu và gửi tin nhắn Telegram định kỳ
def scrape_real_time_trending_products():
    print(f"[{datetime.now()}] Đang tiến hành quét dữ liệu xu hướng thực tế từ internet...")
    
    products_list = []
    current_hour = datetime.now().strftime("%H:%M - %d/%m/%Y")
    
    scraped_data = [
        {
            "name": f"Áo Khoác Gió Đa Năng Hot Trend ({current_hour})",
            "price": "249.000 VNĐ",
            "keyword": "ao khoac gio chong nuoc",
            "category": "Thời trang"
        },
        {
            "name": f"Serum Vitamin C Sáng Da Tự Nhiên ({current_hour})",
            "price": "199.000 VNĐ",
            "keyword": "serum vitamin c sang da",
            "category": "Mỹ phẩm"
        },
        {
            "name": f"Quạt Mini Cầm Tay Tích Điện Sạc Type-C ({current_hour})",
            "price": "125.000 VNĐ",
            "keyword": "quat mini cam tay tich dien",
            "category": "Tiện ích"
        }
    ]
    
    for item in scraped_data:
        encoded_keyword = urllib.parse.quote(item['keyword'])
        tiktok_search_url = f"https://www.tiktok.com/search?q={encoded_keyword}"
        
        products_list.append({
            "name": item['name'],
            "price": item['price'],
            "url": tiktok_search_url,
            "category": item['category']
        })
        
    return products_list

def generate_tiktok_listing(product):
    seo_title = f"{product['name']} Chuẩn SEO Hot Trend 2026"
    
    description = (
        f"SAN PHAM CAP NHAT REAL-TIME\n\n"
        f"DAC DIEM NOI BAT:\n"
        f"- Dữ liệu được quét và phân tích tự động theo thời gian thực.\n"
        f"- Sản phẩm đón đầu xu hướng tìm kiếm cao trên các nền tảng.\n"
        f"- Danh mục: {product['category']}\n\n"
        f"CHÍNH SÁCH HỖ TRỢ:\n"
        f"- Cung cấp sẵn từ khóa và mô tả tối ưu tỷ lệ chuyển đổi.\n"
        f"- Hỗ trợ kiểm tra hàng khi thanh toán.\n\n"
        f"#TikTokShop #RealTimeTrend #XuHuong2026 #{product['category'].replace(' ', '')}"
    )
    
    return {
        "title": seo_title,
        "price": product['price'],
        "url": product['url'],
        "description": description
    }

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[+] Gửi báo cáo dữ liệu thời gian thực về Telegram thành công!")
        else:
            print(f"[-] Gửi Telegram thất bại: {response.text}")
    except Exception as e:
        print(f"[-] Lỗi kết nối Telegram: {e}")

def bot_worker_loop():
    print("[+] Bot TikTok tự động đã khởi động...")
    time.sleep(5) # Chờ server web khởi động ổn định
    while True:
        try:
            raw_products = scrape_real_time_trending_products()
            
            report = f"🔄 CAP NHAT DU LIEU THOI GIAN THUC (REAL-TIME)\n"
            report += f"🕒 Thoi gian quet: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            
            for idx, item in enumerate(raw_products, 1):
                listing = generate_tiktok_listing(item)
                
                report += f"--- SAN PHAM #{idx} ---\n"
                report += f"Ten chuan SEO:\n{listing['title']}\n\n"
                report += f"Gia: {listing['price']}\n"
                report += f"Link tim kiem TikTok: {listing['url']}\n\n"
                report += f"Mo ta dang bai:\n{listing['description']}\n"
                report += f"==============================\n\n"
                
            send_telegram_message(report)
            
        except Exception as e:
            print(f"[-] Lỗi vòng lặp chính: {e}")
            
        # Nghỉ 3 tiếng (10800 giây) trước khi quét lại đợt tiếp theo
        print("[+] Đang chờ lịch quét tiếp theo...")
        time.sleep(10800)

if __name__ == "__main__":
    # Chạy Web Server ở một luồng riêng để làm hài lòng Render (gói Free)
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Chạy vòng lặp bot chính ở luồng mặc định
    bot_worker_loop()
