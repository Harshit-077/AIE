import yfinance as yf
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

class StockMarketBot:
    def __init__(self):
        self.indicators = {
            'SMA': self.calculate_sma,
            'RSI': self.calculate_rsi,
            'MACD': self.calculate_macd
        }
    
    def get_stock_data(self, symbol, period='1mo'):
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def calculate_sma(self, data, window=20):
        """Calculate Simple Moving Average"""
        return data['Close'].rolling(window=window).mean()

    def calculate_rsi(self, data, periods=14):
        """Calculate Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, data):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal

    def get_market_insights(self, symbol):
        """Generate market insights for a given stock symbol"""
        data = self.get_stock_data(symbol)
        if data is None or data.empty:
            return None

        try:
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            price_change = ((current_price - prev_close) / prev_close) * 100

            # Calculate indicators
            sma_20 = self.calculate_sma(data).iloc[-1]
            rsi = self.calculate_rsi(data).iloc[-1]
            macd_line, signal_line = self.calculate_macd(data)
            macd_value = macd_line.iloc[-1]
            signal_value = signal_line.iloc[-1]

            # Generate insights
            insights = [
                ["Metric", "Value", "Analysis"],
                ["Current Price", f"${current_price:.2f}", f"{price_change:+.2f}% from previous close"],
                ["SMA (20)", f"${sma_20:.2f}", "Bullish" if current_price > sma_20 else "Bearish"],
                ["RSI (14)", f"{rsi:.2f}", self._interpret_rsi(rsi)],
                ["MACD", f"{macd_value:.2f}", self._interpret_macd(macd_value, signal_value)]
            ]

            return tabulate(insights, headers="firstrow", tablefmt="grid")
        except (IndexError, KeyError) as e:
            print(f"Error processing data for {symbol}: Insufficient data points")
            return None

    def _interpret_rsi(self, rsi):
        if rsi > 70:
            return "Overbought - Consider Selling"
        elif rsi < 30:
            return "Oversold - Consider Buying"
        else:
            return "Neutral"

    def _interpret_macd(self, macd, signal):
        if macd > signal:
            return "Bullish Signal"
        else:
            return "Bearish Signal"

def main():
    bot = StockMarketBot()
    while True:
        symbol = input("\nEnter stock symbol (or 'quit' to exit): ").upper()
        if symbol.lower() == 'quit':
            break

        print(f"\nFetching market insights for {symbol}...")
        insights = bot.get_market_insights(symbol)
        if insights:
            print(f"\nMarket Insights for {symbol}:")
            print(insights)
        else:
            print(f"Could not fetch data for {symbol}")

if __name__ == "__main__":
    main()