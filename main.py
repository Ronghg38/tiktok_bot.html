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

# 1 giờ gửi một lần (3600 giây)
AUTO_INTERVAL_SECONDS = int(os.environ.get("AUTO_INTERVAL_SECONDS", 3600))

DB_PATH = os.environ.get("DB_PATH", "cauturong_market.sqlite3")
VN_TZ = timezone(timedelta(hours=7))

CHOGIA_MOPS_URL = "https://chogia.vn/gia-xang-dau-singapore-hom-nay-38348/"
STARFISH_MOPS_URL = "https://starfishmyanmar.com/market-price"
GOLD_OFFSET = float(os.environ.get("GOLD_OFFSET", -10.36))

# Tùy chỉnh qua Environment Variables trên Render (nếu để trống sẽ tự tính từ SQLite)
CUSTOM_DELTA_RON92 = os.environ.get("DELTA_USD_RON92", "")
CUSTOM_DELTA_RON95 = os.environ.get("DELTA_USD_RON95", "")
CUSTOM_DELTA_D0 = os.environ.get("DELTA_USD_D0", "")

CUSTOM_DIFF_RON92 = os.environ.get("DIFF_LINE_RON92", "")
CUSTOM_DIFF_RON95 = os.environ.get("DIFF_LINE_RON95", "")
CUSTOM_DIFF_D0 = os.environ.get("DIFF_LINE_D0", "")

DELAY_NOTICE = os.environ.get(
    "DELAY_NOTICE",
    "(Dữ liệu tự động mỗi 60 phút. Dùng lệnh /checknow hoặc /giatien để kiểm tra ngay)",
)

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


def now_vn_dt():
    return datetime.now(VN_TZ)


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
            (now_vn_dt().strftime("%Y-%m-%d %H:%M:%S"), source, symbol, float(price), unit),
        )
        conn.commit()
        conn.close()


def get_previous_price(symbol):
    """Lấy giá gần nhất trước bản ghi vừa lưu để tính phần trăm và chênh lệch."""
    with db_lock:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT price FROM market_snapshots
            WHERE symbol = ?
            ORDER BY id DESC
            LIMIT 1 OFFSET 1
            """,
            (symbol,),
        )
        row = cur.fetchone()
        conn.close()
        return float(row[0]) if row else None


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
        "WTI": "CL=F",
        "Brent": "BZ=F",
        "Gold": "GC=F",
    }
    quotes = {}
    for label, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="2d", interval="1h")
            if hist is not None and not hist.empty:
                last_price = float(hist["Close"].dropna().iloc[-1])
                if label == "Gold":
                    last_price += GOLD_OFFSET
                quotes[label] = round(last_price, 2)
        except Exception as e:
            print(f"[{BOT_ID}] Lỗi yfinance {sym}: {e}")
    return quotes


def format_platts_delta(current_val, prev_val, custom_delta):
    if custom_delta.strip():
        return custom_delta.strip()
    if current_val is None or prev_val is None:
        return "$0.00"
    diff = current_val - prev_val
    if diff < 0:
        return f"-${abs(diff):.2f}"
    return f"+${diff:.2f}"


def format_diff_line(current_val, prev_val, custom_diff):
    if custom_diff.strip():
        return custom_diff.strip()
    if current_val is None or prev_val is None or prev_val == 0:
        return "chưa có biến động so với kỳ trước"
    diff_usd = current_val - prev_val
    pct = (diff_usd / prev_val) * 100.0
    direction = "tăng" if diff_usd > 0 else ("giảm" if diff_usd < 0 else "đi ngang")
    usd_sign = "+" if diff_usd > 0 else ("-" if diff_usd < 0 else "")
    pct_sign = "+" if pct > 0 else ""
    return f"{direction} ({usd_sign}${abs(diff_usd):.2f}) ({pct_sign}{pct:.2f}%)"


def render_fuel_block(title, current_val, prev_val, custom_delta, custom_diff):
    if current_val is None:
        return [
            f"*{title}*",
            "▪ Platts Live : _Đang đồng bộ..._",
            "▪ Chênh lệch : _Chưa có dữ liệu_",
            "",
        ]
    delta_str = format_platts_delta(current_val, prev_val, custom_delta)
    diff_str = format_diff_line(current_val, prev_val, custom_diff)
    return [
        f"*{title}*",
        f"▪ Platts Live : `${current_val:.2f}` `({delta_str})`",
        f"▪ Chênh lệch : *{diff_str}*",
        "",
    ]


def build_market_report():
    now_vn = now_vn_dt()
    time_full = now_vn.strftime("%H:%M:%S %d/%m/%Y")

    mops_cg = fetch_mops_chogia()
    mops_sf = fetch_mops_starfish()
    sf_prices = parse_starfish_mops(mops_sf)
    yf_quotes = fetch_yf_quotes()

    ron92_val = mops_cg.get("RON92") or sf_prices.get("RON92")
    ron95_val = mops_cg.get("RON95") or sf_prices.get("RON95")
    diesel_val = mops_cg.get("DIESEL") or mops_cg.get("GASOIL") or sf_prices.get("DIESEL")

    prev_ron92 = get_previous_price("RON92")
    prev_ron95 = get_previous_price("RON95")
    prev_diesel = get_previous_price("DIESEL")

    resolved_mops = {
        "RON92": ron92_val,
        "RON95": ron95_val,
        "DIESEL": diesel_val,
    }
    for sym, val in resolved_mops.items():
        if val is not None:
            src = "ChoGia_MOPS" if sym in mops_cg else "Starfish_Fallback"
            save_snapshot(src, sym, val, "USD/bbl")

    for label, val in yf_quotes.items():
        save_snapshot("yfinance", label, val, "USD")

    lines = [
        f"🔮 *{BOT_ID} — DỰ TÍNH GCS THEO PLATTS TRONG NGÀY*",
        f"🗓️ Cập nhật lúc: `{time_full}` `(GMT+7)`",
        f"🔔 _{DELAY_NOTICE}_",
        "────────────────────",
        "",
    ]

    lines.extend(
        render_fuel_block(
            "XĂNG RON 92",
            ron92_val,
            prev_ron92,
            CUSTOM_DELTA_RON92,
            CUSTOM_DIFF_RON92,
        )
    )
    lines.extend(
        render_fuel_block(
            "XĂNG RON 95",
            ron95_val,
            prev_ron95,
            CUSTOM_DELTA_RON95,
            CUSTOM_DIFF_RON95,
        )
    )
    lines.extend(
        render_fuel_block(
            "DẦU DO 0.05S",
            diesel_val,
            prev_diesel,
            CUSTOM_DELTA_D0,
            CUSTOM_DIFF_D0,
        )
    )

    if yf_quotes:
        lines.append("*DẦU THÔ & VÀNG QUỐC TẾ*")
        for label, val in yf_quotes.items():
            prev_q = get_previous_price(label)
            q_diff = ""
            if prev_q is not None and prev_q != 0:
                d = val - prev_q
                pct = (d / prev_q) * 100.0
                d_sign = "+" if d >= 0 else ""
                pct_sign = "+" if pct >= 0 else ""
                q_diff = f" `({d_sign}{d:.2f} | {pct_sign}{pct:.2f}%)`"
            lines.append(f"▪ {label} : `${val:,.2f}`{q_diff}")
        lines.append("")

    lines.append("_Mỗi 1 giờ/lần • Lệnh: `/giatien` • `/checknow`_")
    return "\n".join(lines).strip()


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
    return jsonify(
        {
            "status": "online",
            "bot": BOT_ID,
            "time_vn": now_vn_dt().strftime("%Y-%m-%d %H:%M:%S"),
        }
    ), 200


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
