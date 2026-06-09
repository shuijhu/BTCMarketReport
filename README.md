# BTC Market Report

BTC 加密货币市场分析技能，生成包含价格、技术指标、新闻和交易信号的结构化报告。

## 功能

- 📊 **价格概览** — 实时价格、24h涨跌幅、7日高低
- 📈 **技术指标** — MA7/25/99、RSI(14)、MACD、布林带
- 🔥 **市场情绪** — 短期/中期趋势解读
- 🗞️ **热点新闻** — 来自 Bitcoinist RSS
- 🎯 **关键价位** — 支撑/阻力位
- 💡 **交易建议** — 可执行的多空 Bias

## 数据源

| 数据 | 来源 |
|------|------|
| BTC 价格 | Blockchain.info ticker API |
| K线数据 | CryptoCompare histohour API（无需 API Key） |
| 新闻 | Bitcoinist RSS |

## 配置

在执行前设置代理地址（可选）：

```bash
set BTC_PROXY=http://10.241.0.14:10809
set BTC_PROXY_FALLBACK=http://127.0.0.1:10809
```

## 使用方法

1. **获取价格数据**
```bash
curl -s --connect-timeout 10 "%BTC_PROXY%" "https://blockchain.info/ticker" -o .btc_price.json
```

2. **获取K线数据**
```bash
curl -s --connect-timeout 10 "%BTC_PROXY%" "https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=168" -o .btc_kline.json
```

3. **计算指标**
```bash
python scripts/btc_indicators.py
```

4. **获取新闻**
```bash
curl -s --connect-timeout 10 "%BTC_PROXY%" "https://bitcoinist.com/feed/" -o .btc_news.xml
```

## 输出示例

```
📊 BTC市场报告
🕐 2026-06-09 09:15 (UTC+8)

价格概览
• BTC: $62,684.68 (+0.22% 24h)
• 7日高: $70,857 | 7日低: $59,373

技术信号
• RSI(14): 56.88 🟡
• MACD: 95.21 | Signal: 95.21 | Hist: ≈0 🟡
• MA7: $63,205 | MA25: $63,294 | MA99: $62,033

关键价位
• 支撑: $62,544 / $62,033
• 阻力: $63,719 / $64,088
```

## 文件结构

```
btc-market-report/
├── SKILL.md                    ← 技能定义
└── scripts/
    └── btc_indicators.py       ← 技术指标计算脚本
```

## 许可证

MIT
