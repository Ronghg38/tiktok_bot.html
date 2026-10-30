import MetaTrader5 as mt5
import requests
import pandas as pd
from datetime import datetime
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# ==================== CẤU HÌNH HỆ THỐNG CAUTURONG ====================
TELEGRAM_BOT_TOKEN = "9032299426:AAHlXiRdw-BFO3gKtJ7ruAUPkWpUEU3QbUM"
TELEGRAM_CHAT_ID = "5931570040"
SYMBOL = "GOLDm"  # Hoặc "XAUUSD" tùy thuộc vào sàn của bạn
LOT_SIZE = 0.01
MAGIC_NUMBER = 202610
BOT_ID = "CAUTURONG BOT"

# Cấu hình chiến lược kỹ thuật MA19 & MA59 trên khung M5
TIMEFRAME = mt5.TIMEFRAME_M5
FAST_MA = 19
SLOW_MA = 59

SL_POINTS = 350
TP1_POINTS = 400
TP2_POINTS = 800
# ===================================================================

# Web Server ảo để duy trì Render gói Free không bị sleep/timeout
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gold Trading Bot CAUTURONG is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"@{BOT_ID}\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

def initialize_mt5():
    if not mt5.initialize():
        print(f"Khởi tạo MT5 thất bại, lỗi: {mt5.last_error()}")
        return False
    print(f"[{BOT_ID}] Kết nối MetaTrader 5 thành công!")
    return True

def get_market_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, SLOW_MA + 20)
    if rates is None or len(rates) < SLOW_MA:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['MA19'] = df['close'].rolling(window=FAST_MA).mean()
    df['MA59'] = df['close'].rolling(window=SLOW_MA).mean()
    return df

def manage_open_positions():
    positions = mt5.positions_get(symbol=SYMBOL)
    if positions is None or len(positions) == 0:
        return

    tick = mt5.symbol_info_tick(SYMBOL)
    if not tick:
        return

    for pos in positions:
        if pos.magic == MAGIC_NUMBER:
            current_bid = tick.bid
            current_ask = tick.ask
            
            # Quản lý lệnh MUA (BUY): Chạm TP1 thì kéo SL về giá vào lệnh (Hòa vốn)
            if pos.type == mt5.ORDER_TYPE_BUY:
                tp1_target = pos.price_open + (TP1_POINTS * mt5.symbol_info(SYMBOL).point)
                if current_bid >= tp1_target and pos.sl < pos.price_open:
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "symbol": SYMBOL,
                        "sl": pos.price_open,
                        "tp": pos.tp
                    }
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        send_telegram_alert(
                            f"🛡️ *DỜI SL HÒA VỐN*\n"
                            f"Lệnh: MUA {SYMBOL} | m5\n"
                            f"Anh em đã an toàn, gồng lãi thoải mái nhé!"
                        )
                        
            # Quản lý lệnh BÁN (SELL): Chạm TP1 thì kéo SL về giá vào lệnh (Hòa vốn)
            elif pos.type == mt5.ORDER_TYPE_SELL:
                tp1_target = pos.price_open - (TP1_POINTS * mt5.symbol_info(SYMBOL).point)
                if current_ask <= tp1_target and (pos.sl > pos.price_open or pos.sl == 0):
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "symbol": SYMBOL,
                        "sl": pos.price_open,
                        "tp": pos.tp
                    }
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        send_telegram_alert(
                            f"🛡️ *DỜI SL HÒA VỐN*\n"
                            f"Lệnh: BÁN {SYMBOL} | m5\n"
                            f"Anh em đã an toàn, gồng lãi thoải mái nhé!"
                        )

def execute_trading_strategy():
    df = get_market_data()
    if df is None or len(df) < 3:
        return

    manage_open_positions()

    positions = mt5.positions_get(symbol=SYMBOL, magic=MAGIC_NUMBER)
    if positions and len(positions) > 0:
        return

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    ma19_curr = last_row['MA19']
    ma59_curr = last_row['MA59']
    ma19_prev = prev_row['MA19']
    ma59_prev = prev_row['MA59']
    
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return

    point = mt5.symbol_info(SYMBOL).point

    # --- TÍN HIỆU MUA (BUY): MA19 cắt lên trên MA59 ---
    if ma19_prev <= ma59_prev and ma19_curr > ma59_curr:
        price = tick.ask
        sl = price - (SL_POINTS * point)
        tp1 = price + (TP1_POINTS * point)
        tp2 = price + (TP2_POINTS * point)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": LOT_SIZE,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp2,
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": "CauTuRong_Buy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            send_telegram_alert(
                f"📈 *LỆNH MUA (@CAUTURONG)*\n"
                f"Cặp: {SYMBOL} | m5\n"
                f"Entry: `{price}`\n"
                f"SL: `{sl:.2f}`\n"
                f"TP1: `{tp1:.2f}`\n"
                f"TP2: `{tp2:.2f}`"
            )

    # --- TÍN HIỆU BÁN (SELL): MA19 cắt xuống dưới MA59 ---
    elif ma19_prev >= ma59_prev and ma19_curr < ma59_curr:
        price = tick.bid
        sl = price + (SL_POINTS * point)
        tp1 = price - (TP1_POINTS * point)
        tp2 = price - (TP2_POINTS * point)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": LOT_SIZE,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp2,
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": "CauTuRong_Sell",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            send_telegram_alert(
                f"📉 *LỆNH BÁN (@CAUTURONG)*\n"
                f"Cặp: {SYMBOL} | m5\n"
                f"Entry: `{price}`\n"
                f"SL: `{sl:.2f}`\n"
                f"TP1: `{tp1:.2f}`\n"
                f"TP2: `{tp2:.2f}`"
            )

def bot_worker_loop():
    if not initialize_mt5():
        return
        
    send_telegram_alert(f"🚀 *Bot giao dịch Vàng CAUTURONG đã khởi động thành công!*")
    
    while True:
        try:
            execute_trading_strategy()
        except Exception as e:
            print(f"Lỗi vòng lặp: {e}")
        time.sleep(20)

if __name__ == "__main__":
    # Chạy HTTP Server ẩn để đáp ứng yêu cầu của Web Service trên Render
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Chạy vòng lặp bot chính
    bot_worker_loop()
