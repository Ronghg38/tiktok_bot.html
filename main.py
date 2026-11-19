import os
import re
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

# Mặc định 1 giờ gửi một lần (3600 giây)
AUTO_INTERVAL_SECONDS = int(os.environ.get("AUTO_INTERVAL_SECONDS", 3600))

DB_PATH = os.environ.get("DB_PATH", "cauturong_market.sqlite3")
VN_TZ = timezone(timedelta(hours=7))

CHOGIA_MOPS_URL = "https://chogia.vn/gia-xang-dau-singapore-hom-nay-38348/"
STARFISH_MOPS_URL = "https://starfishmyanmar.com/market-price"
GOLD_OFFSET = float(os.environ.get("GOLD_OFFSET", -10.36))

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
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
    """Lấy giá xăng dầu MOPS Singapore từ ChoGia (RON92, RON95, Diesel, Jet)."""
    data = {}
    try:
        resp = requests.get(CHOGIA_MOPS_URL, headers=BROWSER_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = " ".join(soup.get_text(" ").split())

        key_map = [
            (["ron 95", "ron95"], "RON95"),
            (["ron 92", "ron92"], "RON92"),
            (["diesel", "gasoil"], "DIESEL"),
            (["jet"], "JET"),
        ]
        for patterns, norm_key in key_map:
            if norm_key in data:
                continue
            for pat in patterns:
                idx = text.lower().find(pat)
                if idx != -1:
                    snippet = text[idx : idx + 100]
                    for token in snippet.replace(",", ".").split():
                        cleaned = token.strip("$:()%-")
                        try:
                            val = float(cleaned)
                            if 30.0 <= val <= 250.0:
                                data[norm_key] = val
                                break
                        except ValueError:
                            continue
                if norm_key in data:
                    break
    except Exception as e:
        print(f"[{BOT_ID}] Lỗi lấy dữ liệu ChoGia: {e}")
    return data


def fetch_mops_starfish():
    """Lấy dữ liệu tham chiếu giá thị trường/nhiên liệu từ Starfish."""
    found = {}
    try:
        resp = requests.get(STARFISH_MOPS_URL, headers=BROWSER_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for row in soup.find_all(["tr", "li", "p", "div"]):
            line = " ".join(row.get_text(" ").split())
            if len(line) > 140:
                continue
            low = line.lower()
            if any(k in low for k in ["ron92", "ron 92", "ron95", "ron 95", "diesel", "gasoil", "jet"]):
                found[line[:70]] = line
                if len(found) >= 8:
                    break
    except Exception as e:
        print(f"[{BOT_ID}] Lỗi lấy dữ liệu Starfish: {e}")
    return found


def parse_starfish_mops(mops_sf):
    """Trích xuất giá MOPS USD/BBL (RON92, RON95, DIESEL) từ dữ liệu Starfish."""
    extracted = {}
    for _, text in mops_sf.items():
        low = text.lower()
        bbl_match = re.search(r"usd/bbl[^0-9]*(\d+(?:\.\d{1,4})?)", low)
        if bbl_match:
            val = float(bbl_match.group(1))
        else:
            nums = re.findall(r"\b(\d+(?:\.\d{1,4})?)\b", text)
            float_nums = [float(n) for n in nums if 25.0 <= float(n) <= 250.0]
            if not float_nums:
                continue
            val = float_nums[0]

        if not (25.0 <= val <= 250.0):
            continue

        if ("ron 95" in low or "ron95" in low) and "RON95" not in extracted:
            extracted["RON95"] = val
        elif ("ron 92" in low or "ron92" in low) and "RON92" not in extracted:
            extracted["RON92"] = val
        elif ("diesel" in low or "gasoil" in low) and "DIESEL" not in extracted:
            extracted["DIESEL"] = val
    return extracted


def fetch_yf_quotes():
    """Lấy giá dầu WTI (CL=F), Brent (BZ=F) và Vàng (GC=F) qua yfinance."""
    tickers = {
        "WTI (CL=F)": "CL=F",
        "Brent (BZ=F)": "BZ=F",
        "Gold (GC=F)": "GC=F",
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


def build_market_report():
    mops_cg = fetch_mops_chogia()
    mops_sf = fetch_mops_starfish()
    sf_prices = parse_starfish_mops(mops_sf)
    yf_quotes = fetch_yf_quotes()

    ron95_usd = mops_cg.get("RON95") or sf_prices.get("RON95")
    ron92_usd = mops_cg.get("RON92") or sf_prices.get("RON92")
    diesel_usd = mops_cg.get("DIESEL") or mops_cg.get("GASOIL") or sf_prices.get("DIESEL")
    jet_usd = mops_cg.get("JET")

    resolved_mops = {
        "RON95": ron95_usd,
        "RON92": ron92_usd,
        "DIESEL": diesel_usd,
        "JET": jet_usd,
    }
    for sym, val in resolved_mops.items():
        if val is not None:
            src = "ChoGia_MOPS" if sym in mops_cg else "Starfish_Fallback"
            save_snapshot(src, sym, val, "USD/bbl")

    for label, val in yf_quotes.items():
        save_snapshot("yfinance", label, val, "USD")

    lines = [
        f"🛢️ *{BOT_ID} — BẢNG GIÁ PLATTS & DẦU*",
        f"🕒 Cập nhật (VN): `{now_vn_str()}`",
        "────────────────────",
        "*📌 MỐC PLATTS / MOPS SINGAPORE (USD/thùng):*",
    ]

    platts_items = [
        ("Xăng RON 95", ron95_usd, "RON95" in mops_cg),
        ("Xăng RON 92", ron92_usd, "RON92" in mops_cg),
        ("Dầu Diesel 0.05S", diesel_usd, ("DIESEL" in mops_cg or "GASOIL" in mops_cg)),
        ("Nhiên liệu bay Jet A1", jet_usd, "JET" in mops_cg),
    ]
    has_platts = False
    for name, val, from_cg in platts_items:
        if val is not None:
            has_platts = True
            tag = "" if from_cg else " _(Starfish)_"
            lines.append(f"• {name}: *{val:.2f}* USD/bbl{tag}")
    if not has_platts:
        lines.append("• Đang đồng bộ dữ liệu Platts...")

    if yf_quotes:
        lines.append("")
        lines.append("*📈 DẦU THÔ & VÀNG THẾ GIỚI:*")
        for k, v in yf_quotes.items():
            lines.append(f"• {k}: *{v:,.2f}* USD")

    if mops_sf:
        lines.append("")
        lines.append("*🌐 THAM CHIẾU STARFISH:*")
        for _, detail in list(mops_sf.items())[:3]:
            lines.append(f"• `{detail}`")

    lines.append("────────────────────")
    lines.append("_Tự động cập nhật mỗi 1 giờ • Lệnh: `/giatien` • `/checknow`_")
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
    """Tự động gửi báo cáo mỗi 1 giờ (AUTO_INTERVAL_SECONDS = 3600)."""
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
