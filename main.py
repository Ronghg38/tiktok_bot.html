import os
import time
import sqlite3
import threading
from datetime import datetime, timezone, timedelta

import requests
import yfinance as yf
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

# ==================== CẤU HÌNH HỆ THỐNG CAUTURONG ====================
TELEGRAM_BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN", "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
)
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5931570040")
BOT_ID = os.environ.get("BOT_ID", "CAUTURONG BOT")
PORT = int(os.environ.get("PORT", 10000))
AUTO_INTERVAL_SECONDS = int(os.environ.get("AUTO_INTERVAL_SECONDS", 3600))

DB_PATH = os.environ.get("DB_PATH", "cauturong_market.sqlite3")
VN_TZ = timezone(timedelta(hours=7))

CHOGIA_MOPS_URL = "https://chogia.vn/gia-xang-dau-singapore-hom-nay-38348/"
STARFISH_MOPS_URL = "https://starfishmyanmar.com/market-price"

# ==================== CẤU HÌNH QUY ĐỔI PLATTS & BÁN LẺ VND ====================
LITERS_PER_BARREL = 158.9873
DEFAULT_USD_VND = float(os.environ.get("USD_VND_RATE", 25450))
GOLD_OFFSET = float(os.environ.get("GOLD_OFFSET", -10.36))

# Tổng thuế nhập khẩu, TTĐB, BVMT, VAT & chi phí định mức (VND/lít) để ước tính giá bán lẻ
RETAIL_TAX_COST_VND = {
    "RON95": float(os.environ.get("COST_RON95_VND", 8650)),
    "RON92": float(os.environ.get("COST_RON92_VND", 8150)),
    "DIESEL": float(os.environ.get("COST_DIESEL_VND", 4950)),
}

app = Flask(__name__)
db_lock = threading.Lock()


def now_vn_str():
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                source TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                unit TEXT DEFAULT 'USD/bbl'
            )
            """
        )
        conn.commit()
        conn.close()


def save_snapshot(source, symbol, price, unit="USD/bbl"):
    if price is None:
        return
    with db_lock:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO market_snapshots (recorded_at, source, symbol, price, unit)
            VALUES (?, ?, ?, ?, ?)
            """,
            (now_vn_str(), source, symbol, float(price), unit),
        )
        conn.commit()
        conn.close()


def fetch_mops_chogia():
    """Lấy giá xăng dầu MOPS Singapore từ ChoGia (RON92, RON95, Diesel10, Jet)."""
    headers = {"User-Agent": "Mozilla/5.0"}
    data = {}
    try:
        resp = requests.get(CHOGIA_MOPS_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = " ".join(soup.get_text(" ").split())

        for key in ["RON 92", "RON92", "RON 95", "RON95", "Diesel", "Gasoil", "Jet"]:
            idx = text.lower().find(key.lower())
            if idx != -1:
                snippet = text[idx : idx + 80]
                for token in snippet.replace(",", ".").split():
                    cleaned = token.strip("$:()%-")
                    try:
                        val = float(cleaned)
                        if 30.0 <= val <= 250.0:
                            norm_key = key.replace(" ", "").upper()
                            if norm_key not in data:
                                data[norm_key] = val
                            break
                    except ValueError:
                        continue
    except Exception as e:
        print(f"[{BOT_ID}] Lỗi lấy dữ liệu ChoGia: {e}")
    return data


def fetch_mops_starfish():
    """Lấy dữ liệu tham chiếu giá thị trường/nhiên liệu từ Starfish."""
    headers = {"User-Agent": "Mozilla/5.0"}
    found = {}
    try:
        resp = requests.get(STARFISH_MOPS_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for row in soup.find_all(["tr", "li", "p"]):
            line = " ".join(row.get_text(" ").split())
            low = line.lower()
            if any(k in low for k in ["ron92", "ron 92", "ron95", "ron 95", "diesel", "gasoil", "jet"]):
                found[line[:60]] = line
                if len(found) >= 6:
                    break
    except Exception as e:
        print(f"[{BOT_ID}] Lỗi lấy dữ liệu Starfish: {e}")
    return found


def fetch_yf_quotes():
    """Lấy giá dầu WTI (CL=F), Brent (BZ=F), Vàng (GC=F) và tỷ giá USD/VND (VND=X)."""
    tickers = {
        "WTI (CL=F)": "CL=F",
        "Brent (BZ=F)": "BZ=F",
        "Gold (GC=F)": "GC=F",
        "USD/VND": "VND=X",
    }
    quotes = {}
    for label, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="2d", interval="1h")
            if hist is not None and not hist.empty:
                last_price = float(hist["Close"].dropna().iloc[-1])
                if label == "Gold (GC=F)":
                    last_price += GOLD_OFFSET
                quotes[label] = round(last_price, 2)
        except Exception as e:
            print(f"[{BOT_ID}] Lỗi yfinance {sym}: {e}")
    return quotes


def calc_vnd_retail_estimate(usd_per_bbl, usd_vnd_rate, fuel_type):
    """Quy đổi giá MOPS (USD/thùng) sang giá nhập CIF và giá bán lẻ ước tính (VND/lít)."""
    cif_vnd_per_liter = (usd_per_bbl * usd_vnd_rate) / LITERS_PER_BARREL
    extra_cost = RETAIL_TAX_COST_VND.get(fuel_type, 8000)
    retail_vnd_per_liter = cif_vnd_per_liter + extra_cost
    return round(cif_vnd_per_liter), round(retail_vnd_per_liter)


def build_market_report():
    mops_cg = fetch_mops_chogia()
    mops_sf = fetch_mops_starfish()
    yf_quotes = fetch_yf_quotes()

    usd_vnd = yf_quotes.get("USD/VND", DEFAULT_USD_VND)

    for sym, val in mops_cg.items():
        save_snapshot("ChoGia_MOPS", sym, val, "USD/bbl")
    for label, val in yf_quotes.items():
        unit = "VND" if label == "USD/VND" else "USD"
        save_snapshot("yfinance", label, val, unit)

    ron95_usd = mops_cg.get("RON95")
    ron92_usd = mops_cg.get("RON92")
    diesel_usd = mops_cg.get("DIESEL") or mops_cg.get("GASOIL")
    jet_usd = mops_cg.get("JET")

    lines = [
        f"🛢️ *{BOT_ID} — BẢNG GIÁ PLATTS & QUY ĐỔI VND*",
        f"🕒 Cập nhật (VN): `{now_vn_str()}`",
        f"💱 Tỷ giá quy đổi: *1 USD = {usd_vnd:,.0f} VND*",
        "────────────────────",
        "*📌 MỐC PLATTS / MOPS SINGAPORE (USD/thùng):*",
    ]

    platts_items = [
        ("Xăng RON 95", ron95_usd),
        ("Xăng RON 92", ron92_usd),
        ("Dầu Diesel 0.05S", diesel_usd),
        ("Nhiên liệu bay Jet A1", jet_usd),
    ]
    has_platts = False
    for name, val in platts_items:
        if val is not None:
            has_platts = True
            lines.append(f"• {name}: *{val:.2f}* USD/bbl")
    if not has_platts:
        lines.append("• Đang đồng bộ dữ liệu Platts từ ChoGia...")

    lines.append("")
    lines.append("*🇻🇳 QUY ĐỔI GIÁ NHẬP & BÁN LẺ ƯỚC TÍNH (VND/lít):*")
    retail_targets = [
        ("Xăng RON 95-III", ron95_usd, "RON95"),
        ("Xăng E5 RON 92", ron92_usd, "RON92"),
        ("Dầu Diesel 0.05S", diesel_usd, "DIESEL"),
    ]
    has_retail = False
    for label, usd_val, code in retail_targets:
        if usd_val is not None:
            has_retail = True
            cif_vnd, est_retail = calc_vnd_retail_estimate(usd_val, usd_vnd, code)
            lines.append(
                f"• {label}: Giá gốc `{cif_vnd:,}đ` → Bán lẻ ~*{est_retail:,} đ/lít*"
            )
    if not has_retail:
        lines.append("• Chưa có dữ liệu MOPS để quy đổi VND.")

    commodity_quotes = {k: v for k, v in yf_quotes.items() if k != "USD/VND"}
    if commodity_quotes:
        lines.append("")
        lines.append("*📈 DẦU THÔ & VÀNG THẾ GIỚI:*")
        for k, v in commodity_quotes.items():
            lines.append(f"• {k}: *{v:,.2f}* USD")

    if mops_sf:
        lines.append("")
        lines.append("*🌐 THAM CHIẾU STARFISH:*")
        for _, detail in list(mops_sf.items())[:3]:
            lines.append(f"• `{detail}`")

    lines.append("────────────────────")
    lines.append("_Lệnh nhanh: `/giatien` • `/checknow`_")
    return "\n".join(lines)


def send_telegram_message(text, chat_id=None):
    target_chat = chat_id or TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.json()
    except Exception as e:
        print(f"[{BOT_ID}] Lỗi gửi Telegram: {e}")
        return {"ok": False, "error": str(e)}


def background_scheduler():
    while True:
        try:
            report = build_market_report()
            send_telegram_message(report, TELEGRAM_CHAT_ID)
        except Exception as e:
            print(f"[{BOT_ID}] Lỗi luồng tự động: {e}")
        time.sleep(AUTO_INTERVAL_SECONDS)


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "online", "bot": BOT_ID, "time_vn": now_vn_str()}), 200


@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = request.get_json(silent=True) or {}
    message = update.get("message") or update.get("edited_message") or {}
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = (message.get("text") or "").strip().lower()

    if not chat_id or not text:
        return jsonify({"ok": True}), 200

    cmd = text.split()[0].split("@")[0]
    if cmd in ["/giatien", "/checknow", "/start"]:
        report = build_market_report()
        send_telegram_message(report, chat_id)
    return jsonify({"ok": True}), 200


init_db()
threading.Thread(target=background_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
