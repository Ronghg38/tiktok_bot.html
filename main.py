import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime

def get_real_sjc_gold():
    try:
        # Nguồn XML chính thức của SJC
        url = "https://sjc.com.vn/xml/tygiavang.xml"
        response = requests.get(url, timeout=10)
        tree = ET.fromstring(response.content)
        
        # Tìm giá vàng SJC (Hồ Chí Minh/Toàn quốc)
        for city in tree.findall(".//city"):
            if "Hồ Chí Minh" in city.get("name", ""):
                for item in city.findall("item"):
                    if item.get("type") == "Vàng SJC 1L - 10L - 1KG":
                        buy = f"{float(item.get('buy', 0)):,.2f} triệu/lượng"
                        sell = f"{float(item.get('sell', 0)):,.2f} triệu/lượng"
                        return buy, sell
    except Exception as e:
        print(f"Lỗi lấy giá Vàng: {e}")
    return "Đang cập nhật", "Đang cập nhật"

def get_real_usd_vcb():
    try:
        # Nguồn XML tỷ giá chính thức của Vietcombank
        url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"
        response = requests.get(url, timeout=10)
        tree = ET.fromstring(response.content)
        
        for exrate in tree.findall("Exrate"):
            if exrate.get("CurrencyCode") == "USD":
                sell_rate = exrate.get("Sell")
                return f"{sell_rate} VND"
    except Exception as e:
        print(f"Lỗi lấy giá USD: {e}")
    return "Đang cập nhật"

def get_realtime_market_data():
    current_time_str = datetime.now().strftime('%H:%M - %d/%m/%Y')
    
    # Lấy dữ liệu thực tế từ API/XML
    sjc_buy, sjc_sell = get_real_sjc_gold()
    usd_rate = get_real_usd_vcb()
    
    # Ghi chú: Xăng dầu và nông sản thường không có API mở, 
    # phần này bạn cần cào (scrape) từ các trang như Petrolimex hoặc giacaphe.com.
    # Dưới đây là dữ liệu tĩnh giữ chỗ, bạn có thể áp dụng BeautifulSoup tương tự nếu có cấu trúc web cụ thể.
    data = {
        "time": current_time_str,
        "sjc_buy": sjc_buy,
        "sjc_sell": sjc_sell,
        "usd_vnd": usd_rate,
        "gas_e10_ron95": "23,320 đ/lít",  # Tạm thời điền tĩnh, cần scrape Petrolimex
        "gas_e5": "22,460 đ/lít",         
        "oil_diesel": "20,250 đ/lít",     
        "coffee_robusta": "120,000 đ/kg", # Tạm thời điền tĩnh, cần scrape giacaphe.com
        "pepper": "145,000 đ/kg",         
        "rice_om5451": "8,000 đ/kg"       
    }
    return data
