import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import threading

class StockMarketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Market Analysis")
        self.root.geometry("1200x800")
        
        # Fixed USD to INR conversion rate
        self.usd_to_inr = 83.0  # Using a fixed rate
        self.current_symbol = ""
        self.update_interval = 60000  # Update every 60 seconds
        
        # Create main frames
        self.input_frame = ttk.Frame(root, padding="10")
        self.input_frame.pack(fill=tk.X)
        
        self.title_frame = ttk.Frame(root, padding="5")
        self.title_frame.pack(fill=tk.X)
        self.company_name_label = ttk.Label(self.title_frame, text="", font=("Helvetica", 16, "bold"))
        self.company_name_label.pack()
        
        self.content_frame = ttk.Frame(root, padding="10")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input elements
        ttk.Label(self.input_frame, text="Stock Symbol:").pack(side=tk.LEFT)
        self.symbol_entry = ttk.Entry(self.input_frame, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)
        
        self.period_var = tk.StringVar(value="1mo")
        ttk.Label(self.input_frame, text="Period:").pack(side=tk.LEFT, padx=(10, 0))
        period_combo = ttk.Combobox(self.input_frame, textvariable=self.period_var, 
                                  values=["1d", "5d", "1mo", "3mo", "6mo", "1y"], 
                                  width=5)
        period_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.input_frame, text="Analyze", command=self.analyze_stock).pack(side=tk.LEFT, padx=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.chart_tab = ttk.Frame(self.notebook)
        self.indicators_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.chart_tab, text="Price Chart")
        self.notebook.add(self.indicators_tab, text="Technical Indicators")
        
        # Initialize chart
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize indicators display
        self.indicators_text = tk.Text(self.indicators_tab, wrap=tk.WORD, height=20)
        self.indicators_text.pack(fill=tk.BOTH, expand=True)
        
    def get_stock_data(self, symbol, period):
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            
            if data.empty:
                messagebox.showerror("Error", f"No data available for {symbol}")
                return None
                
            if len(data) < 26:  # Minimum required for MACD calculation
                messagebox.showwarning("Warning", f"Insufficient historical data for {symbol}. Some indicators may not be accurate.")
            
            # Convert USD to INR using fixed rate
            data['Close'] = data['Close'] * self.usd_to_inr
            data['Open'] = data['Open'] * self.usd_to_inr
            data['High'] = data['High'] * self.usd_to_inr
            data['Low'] = data['Low'] * self.usd_to_inr
            
            # Get company name
            company_info = stock.info
            company_name = company_info.get('longName', symbol)
            self.company_name_label.config(text=company_name)
            return data
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_indicators(self, data):
        # Calculate SMA
        sma_20 = data['Close'].rolling(window=20).mean()
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return sma_20, rsi, macd, signal
    
    def plot_chart(self, data):
        self.figure.clear()
        
        # Create price subplot
        ax1 = self.figure.add_subplot(211)
        ax1.plot(data.index, data['Close'], label='Close Price')
        ax1.set_title('Stock Price')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.grid(True)
        ax1.legend()
        
        # Create volume subplot
        ax2 = self.figure.add_subplot(212)
        ax2.bar(data.index, data['Volume'], label='Volume')
        ax2.set_title('Volume')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Volume')
        ax2.grid(True)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_indicators(self, data):
        if len(data) < 2:
            self.indicators_text.delete(1.0, tk.END)
            self.indicators_text.insert(tk.END, "Insufficient data to calculate indicators")
            return
            
        sma_20, rsi, macd, signal = self.calculate_indicators(data)
        
        current_price = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2]
        price_change = ((current_price - prev_close) / prev_close) * 100
        
        # Format indicators text
        indicators_text = f"""Current Price: ₹{current_price:.2f} ({price_change:+.2f}%)

"""
        indicators_text += f"SMA (20): ₹{sma_20.iloc[-1]:.2f}"
        indicators_text += " (Bullish)" if current_price > sma_20.iloc[-1] else " (Bearish)"
        
        indicators_text += f"\n\nRSI (14): {rsi.iloc[-1]:.2f}"
        if rsi.iloc[-1] > 70:
            indicators_text += " (Overbought - Consider Selling)"
        elif rsi.iloc[-1] < 30:
            indicators_text += " (Oversold - Consider Buying)"
        else:
            indicators_text += " (Neutral)"
        
        indicators_text += f"\n\nMACD: {macd.iloc[-1]:.2f}"
        indicators_text += " (Bullish Signal)" if macd.iloc[-1] > signal.iloc[-1] else " (Bearish Signal)"
        
        self.indicators_text.delete(1.0, tk.END)
        self.indicators_text.insert(tk.END, indicators_text)
    
    def auto_update(self):
        if self.current_symbol:
            data = self.get_stock_data(self.current_symbol, self.period_var.get())
            if data is not None and not data.empty:
                self.plot_chart(data)
                self.update_indicators(data)
        self.root.after(self.update_interval, self.auto_update)
    
    def analyze_stock(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showwarning("Warning", "Please enter a stock symbol")
            return
        
        self.current_symbol = symbol
        data = self.get_stock_data(symbol, self.period_var.get())
        if data is not None and not data.empty:
            self.plot_chart(data)
            self.update_indicators(data)
        

def main():
    root = tk.Tk()
    app = StockMarketGUI(root)
    app.auto_update()  # Start auto-update
    root.mainloop()

if __name__ == "__main__":
    main()