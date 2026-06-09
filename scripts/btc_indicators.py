"""BTC Market Report - Technical Indicator Calculator
Usage: python btc_indicators.py
Requires: .btc_price.json (blockchain.info ticker) and .btc_kline.json (CryptoCompare histohour)
"""

import json
import statistics
import sys

PROXY = "http://10.241.0.14:10809"
PROXY_FALLBACK = "http://127.0.0.1:10809"

def sma(arr, n):
    return statistics.mean(arr[-n:])

def ema(arr, n):
    if len(arr) < n:
        return sma(arr, len(arr))
    k = 2/(n+1)
    e = arr[0]
    for v in arr[1:]:
        e = v*k + e*(1-k)
    return e

# --- Load price data (blockchain.info ticker) ---
try:
    with open(".btc_price.json") as f:
        ticker = json.load(f)
    price = ticker["USD"]["last"]
    change_24h = ((price - ticker["USD"].get("15m", price)) / ticker["USD"].get("15m", price) * 100) if "15m" in ticker["USD"] else 0
except Exception as e:
    print(f"ERROR: Failed to load .btc_price.json: {e}")
    sys.exit(1)

# --- Load kline data (CryptoCompare histohour) ---
try:
    with open(".btc_kline.json") as f:
        d = json.load(f)
    closes = [p["close"] for p in d["Data"]["Data"]]
except Exception as e:
    print(f"ERROR: Failed to load .btc_kline.json: {e}")
    sys.exit(1)

# --- Moving Averages ---
ma7  = sma(closes, 7)
ma25 = sma(closes, 25)
ma99 = sma(closes, min(99, len(closes)))

# --- RSI(14) Wilder ---
delta  = [closes[i] - closes[i-1] for i in range(1, len(closes))]
gains  = [d for d in delta if d > 0]
losses = [-d for d in delta if d < 0]
avg_gain = statistics.mean(gains[-14:]) if len(gains) >= 14 else 0
avg_loss = statistics.mean(losses[-14:]) if len(losses) >= 14 else 0
rs = avg_gain / avg_loss if avg_loss else 999
rsi = 100 - (100 / (1 + rs))

# --- MACD ---
macd_line   = ema(closes, 12) - ema(closes, 26)
signal_line = ema([macd_line]*9, 9)
macd_hist   = macd_line - signal_line

# --- Bollinger Bands (MA20) ---
ma20  = sma(closes, 20)
stdev = statistics.stdev(closes[-20:]) if len(closes) >= 20 else 0
bb_upper = ma20 + 2 * stdev
bb_lower = ma20 - 2 * stdev

# --- Support/Resistance (recent 10 bars of last 50) ---
recent = closes[-50:]
support    = min(recent[-10:])
resistance = max(recent[-10:])

# --- 7d high/low ---
high_7d = max(closes)
low_7d  = min(closes)

# --- Output ---
print(f"PRICE={price}")
print(f"CHANGE_24H={change_24h:.2f}")
print(f"HIGH_7D={high_7d}")
print(f"LOW_7D={low_7d}")
print(f"MA7={ma7:.2f}")
print(f"MA25={ma25:.2f}")
print(f"MA99={ma99:.2f}")
print(f"RSI={rsi:.2f}")
print(f"MACD={macd_line:.2f}")
print(f"SIGNAL={signal_line:.2f}")
print(f"HIST={macd_hist:.2f}")
print(f"BB_U={bb_upper:.2f}")
print(f"BB_L={bb_lower:.2f}")
print(f"SUPPORT={support:.2f}")
print(f"RESISTANCE={resistance:.2f}")
