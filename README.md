# Stock Market Insights Bot

A Python-based stock market analysis tool that provides real-time insights and technical indicators for stocks.

## Features

- Real-time stock data fetching using Yahoo Finance API
- Technical indicators calculation (SMA, RSI, MACD)
- Market trend analysis
- User-friendly command-line interface
- Formatted insights display

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the bot:
```bash
python stock_bot.py
```

## Usage

1. When prompted, enter a stock symbol (e.g., AAPL, GOOGL, MSFT)
2. The bot will display:
   - Current price and price change
   - 20-day Simple Moving Average (SMA)
   - Relative Strength Index (RSI)
   - Moving Average Convergence Divergence (MACD)
3. Type 'quit' to exit the program

## Example Output

```
Enter stock symbol: AAPL

Market Insights for AAPL:
+---------------+----------+---------------------------+
| Metric        | Value    | Analysis                 |
+---------------+----------+---------------------------+
| Current Price | $191.45  | +1.23% from previous close|
| SMA (20)      | $189.75  | Bullish                  |
| RSI (14)      | 65.32    | Neutral                  |
| MACD          | 1.45     | Bullish Signal           |
+---------------+----------+---------------------------+
```