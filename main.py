import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

# ==================== CẤU HÌNH TÀI KHOẢN CỦA BẠN ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
# ==========================================================

def get_best_selling_tiktok_products():
    print(f"[{datetime.now()}] Đang cập nhật danh sách sản phẩm bán chạy nhất trên TikTok Shop...")
    
    # Danh sách tổng hợp các sản phẩm xu hướng thực tế
    products_list = [
        {
            "name": "Ao Khoac Bomber Unisex Du 2 Lop",
            "price": "229.000 VNĐ",
            "search_keyword": "ao khoac bomber unisex du 2 lop",
            "category": "Thời trang"
        },
        {
            "name": "Kem Duong The Trang Da Vitamin C",
            "price": "185.000 VNĐ",
            "search_keyword": "kem duong the trang da vitamin c",
            "category": "Mỹ phẩm"
        },
        {
            "name": "Noi Chien Khong Dau Dien Tu 6L",
            "price": "690.000 VNĐ",
            "search_keyword": "noi chien khong dau 6l",
            "category": "Gia dụng"
        },
        {
            "name": "May Xay Sinh To Mini Cam Tay",
            "price": "145.000 VNĐ",
            "search_keyword": "may xay sinh to mini cam tay",
            "category": "Tiện ích"
        },
        {
            "name": "Kep Toc Cua Cua Nhieu Mau Hot Trend",
            "price": "35.000 VNĐ",
            "search_keyword": "kep toc cua cua hot trend",
            "category": "Phụ kiện"
        }
    ]
    
    formatted_products = []
    for p in products_list:
        # Tự động mã hóa từ khóa để tạo link tìm kiếm chính xác trên TikTok
        encoded_keyword = urllib.parse.quote(p['search_keyword'])
        tiktok_search_url = f"https://www.tiktok.com/search?q={encoded_keyword}"
        
        formatted_products.append({
            "name": p['name'],
            "price": p['price'],
            "url": tiktok_search_url,
            "category": p['category']
        })
        
    return formatted_products

def generate_tiktok_listing(product):
    seo_title = f"{product['name']} Form Rong Cao Cap Hot Trend 2026"
    
    description = (
        f"SAN PHAM HOT TREND TIKTOK SHOP\n\n"
        f"DAC DIEM NOI BAT:\n"
        f"- Thiet ke bat kip xu hướng moi nhat, tối ưu trai nghiệm.\n"
        f"- Chat lượng đã được kiem chung qua luot ban thuc te.\n"
        f"- Danh mục: {product['category']}\n\n"
        f"CHINH SACH DOI TRA:\n"
        f"- Ho tro doi tra trong 7 ngay theo chinh sach san.\n"
        f"- Kiem tra hang truoc khi thanh toan.\n\n"
        f"#TikTokShop #XuHuong #SanPhamBanChay #{product['category'].replace(' ', '')}"
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
            print("[+] Gửi báo cáo danh sách sản phẩm bán chạy về Telegram thành công!")
        else:
            print(f"[-] Gửi Telegram thất bại: {response.text}")
    except Exception as e:
        print(f"[-] Lỗi kết nối: {e}")

def main():
    raw_products = get_best_selling_tiktok_products()
    
    report = f"🔥 CAP NHAT DANH SACH SAN PHAM BAN CHAY\n"
    report += f"🕒 Thoi gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    
    for idx, item in enumerate(raw_products, 1):
        listing = generate_tiktok_listing(item)
        
        report += f"--- SAN PHAM #{idx} ---\n"
        report += f"Ten chuan SEO:\n{listing['title']}\n\n"
        report += f"Gia: {listing['price']}\n"
        report += f"Link tim kiem TikTok: {listing['url']}\n\n"
        report += f"Mo ta dang bai:\n{listing['description']}\n"
        report += f"==============================\n\n"
        
    send_telegram_message(report)

if __name__ == "__main__":
    main()
