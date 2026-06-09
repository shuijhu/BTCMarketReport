---
name: btc-market-report
description: "Generate BTC cryptocurrency market report: price, technical indicators (RSI/MACD/MA/BB), news digest, sentiment, and trading levels. Excludes file saving."
---

# BTC Market Report

Generate a structured BTC market analysis report combining on-chain data, technical indicators, news, and trading signals. Output in Telegram-friendly markdown.

## ⚙️ Configuration

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 主代理 | `BTC_PROXY` | `http://10.241.0.14:10809` | SOCKS5 代理地址 |
| 备用代理 | `BTC_PROXY_FALLBACK` | `http://127.0.0.1:10809` | 主代理失败时使用 |
| 新闻源 | `BTC_NEWS_URL` | `https://bitcoinist.com/feed/` | RSS feed 地址 |

> 设置环境变量或在执行命令前修改脚本中的 `PROXY` / `PROXY_FALLBACK` 常量。

## Data Sources

| 数据 | 来源 | 备注 |
|------|------|------|
| BTC价格 | Blockchain.info ticker API | 主价格源（无认证） |
| BTC K线 | CryptoCompare `histohour` API | 7日小时数据，无API key |
| 新闻 | Bitcoinist RSS | 备用: `https://cryptonews.net/` |

> ⚠️ **CoinGecko 在本环境下无法访问**，实际使用 Blockchain.info + CryptoCompare 组合。

## Workflow

### Step 1 — Fetch BTC Price

```bash
curl -s --connect-timeout 10 "%BTC_PROXY%" "https://blockchain.info/ticker" -o .btc_price.json
```

Price comes from `USD.last` field.

### Step 2 — Fetch K-line (7 days hourly)

```bash
curl -s --connect-timeout 10 "%BTC_PROXY%" "https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=168&api_key=***" -o .btc_kline.json
```

> API key 占位符 `***`，实际请求去掉 `&api_key=***` 后缀即可。

### Step 3 — Calculate Technical Indicators

```python
import json, statistics

# Load price
with open(".btc_price.json") as f:
    ticker = json.load(f)
price = ticker["USD"]["last"]

# Load kline
with open(".btc_kline.json") as f:
    d = json.load(f)
closes = [p["close"] for p in d["Data"]["Data"]]
highs  = [p["high"]  for p in d["Data"]["Data"]]
lows   = [p["low"]   for p in d["Data"]["Data"]]

def sma(arr, n): return statistics.mean(arr[-n:])
def ema(arr, n):
    if len(arr) < n: return sma(arr, len(arr))
    k = 2/(n+1)
    e = arr[0]
    for v in arr[1:]: e = v*k + e*(1-k)
    return e

ma7  = sma(closes, 7)
ma25 = sma(closes, 25)
ma99 = sma(closes, min(99, len(closes)))

# RSI(14) Wilder
delta  = [closes[i]-closes[i-1] for i in range(1, len(closes))]
gains  = [d for d in delta if d > 0]
losses = [-d for d in delta if d < 0]
avg_gain = statistics.mean(gains[-14:]) if len(gains) >= 14 else 0
avg_loss = statistics.mean(losses[-14:]) if len(losses) >= 14 else 0
rs = avg_gain/avg_loss if avg_loss else 999
rsi = 100 - 100/(1+rs)

# MACD
macd_line   = ema(closes, 12) - ema(closes, 26)
signal_line = ema([macd_line]*9, 9)
macd_hist   = macd_line - signal_line

# Bollinger Bands MA20
ma20  = sma(closes, 20)
stdev = statistics.stdev(closes[-20:]) if len(closes) >= 20 else 0
bb_u  = ma20 + 2*stdev
bb_l  = ma20 - 2*stdev

# Support / Resistance (recent 10 bars)
recent = closes[-50:]
support    = min(recent[-10:])
resistance = max(recent[-10:])

print(f"PRICE={price}")
print(f"MA7={ma7:.2f} MA25={ma25:.2f} MA99={ma99:.2f}")
print(f"RSI={rsi:.2f} MACD={macd_line:.2f} SIGNAL={signal_line:.2f} HIST={macd_hist:.2f}")
print(f"BB_U={bb_u:.2f} BB_L={bb_l:.2f}")
print(f"SUPPORT={support:.2f} RESISTANCE={resistance:.2f}")
```

Save as `scripts/btc_indicators.py` and run: `python scripts/btc_indicators.py`

### Step 4 — Fetch News

```bash
curl -s --connect-timeout 10 "%BTC_PROXY%" "https://bitcoinist.com/feed/" -o .btc_news.xml
```

Parse top 5 items with title + link using regex or Python.

### Step 5 — Compose Report

Assemble sections in markdown:

1. **📊 价格概览** — price, 24h change, 7d high/low, volume
2. **📈 技术指标** — table of MA7/25/99, RSI, MACD, BB; color-coded signals
3. **🔥 市场情绪** — short/long-term trend interpretation
4. **🗞️ 热点新闻** — top 5 items
5. **🎯 关键价位** — support and resistance
6. **💡 交易建议** — short/mid-term bias

## Signal Color Coding

| 指标 | 🟢 看多 | 🔴 看空 |
|------|---------|---------|
| RSI | < 35 超卖 | > 65 超买 |
| MACD柱 | > 0 金叉 | < 0 死叉 |
| 价格 vs MA7 | > MA7 | < MA7 |
| 价格 vs MA25 | > MA25 | < MA25 |

## Error Handling

- Price API fails → try `https://api.coingecko.com/api/v3/coins/bitcoin` as fallback
- Kline API fails → try Binance `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=168`
- Proxy timeout → try `%BTC_PROXY_FALLBACK%`
- News fetch fails → skip news section, note "新闻源暂时不可用"
- Always note which data source was used in footer

## Notes

- 本技能从 `D:\skills\btc-market-report` 加载
- `scripts/btc_indicators.py` 需要 `.btc_price.json` 和 `.btc_kline.json` 同目录
- CryptoCompare API 无需 key，`api_key=***` 参数可删除
