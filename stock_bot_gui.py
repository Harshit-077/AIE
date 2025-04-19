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
        
        # Theme and styling
        self.style = ttk.Style()
        self.is_dark_theme = False
        
        # Fixed USD to INR conversion rate
        self.usd_to_inr = 83.0  # Using a fixed rate
        self.current_symbol = ""
        self.update_interval = 60000  # Update every 60 seconds
        
        # Create main frames
        self.input_frame = ttk.Frame(root, padding="10", style='Card.TFrame')
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.title_frame = ttk.Frame(root, padding="5", style='Card.TFrame')
        self.title_frame.pack(fill=tk.X, padx=10, pady=5)
        self.company_name_label = ttk.Label(self.title_frame, text="", font=("Helvetica", 16, "bold"), style='Title.TLabel')
        self.company_name_label.pack()
        
        # Theme toggle button
        self.theme_button = ttk.Button(self.input_frame, text="🌙", width=3, command=self.toggle_theme)
        self.theme_button.pack(side=tk.RIGHT, padx=5)
        
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
        
        analyze_button = ttk.Button(self.input_frame, text="Analyze", command=self.analyze_stock, style='Accent.TButton')
        analyze_button.pack(side=tk.LEFT, padx=10)
        
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
        self.indicators_text = tk.Text(self.indicators_tab, wrap=tk.WORD, height=20, font=("Helvetica", 11))
        self.indicators_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Apply initial theme after all widgets are created
        self.setup_theme()
        
    def setup_theme(self):
        # Light theme colors
        self.light_theme = {
            'bg': '#ffffff',
            'fg': '#333333',
            'accent': '#007bff',
            'card': '#f8f9fa'
        }
        
        # Dark theme colors
        self.dark_theme = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'accent': '#0d6efd',
            'card': '#2d2d2d'
        }
        
        # Apply initial theme
        self.apply_theme(self.light_theme)
    
    def apply_theme(self, theme):
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('Card.TFrame', background=theme['card'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('Title.TLabel', background=theme['card'], foreground=theme['fg'])
        self.style.configure('TButton', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('Accent.TButton', background=theme['accent'], foreground='white')
        
        self.root.configure(bg=theme['bg'])
        self.indicators_text.configure(bg=theme['card'], fg=theme['fg'], insertbackground=theme['fg'])
        
        # Update chart colors
        if hasattr(self, 'figure'):
            self.figure.set_facecolor(theme['bg'])
            for ax in self.figure.get_axes():
                ax.set_facecolor(theme['bg'])
                ax.tick_params(colors=theme['fg'])
                ax.xaxis.label.set_color(theme['fg'])
                ax.yaxis.label.set_color(theme['fg'])
                ax.title.set_color(theme['fg'])
            self.canvas.draw()
    
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_button.configure(text='☀️' if self.is_dark_theme else '🌙')
        self.apply_theme(self.dark_theme if self.is_dark_theme else self.light_theme)
        
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
        # Calculate SMA and Bollinger Bands
        sma_20 = data['Close'].rolling(window=20).mean()
        std_dev = data['Close'].rolling(window=20).std()
        bollinger_upper = sma_20 + (std_dev * 2)
        bollinger_lower = sma_20 - (std_dev * 2)
        
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
        
        return sma_20, rsi, macd, signal, bollinger_upper, bollinger_lower
    
    def plot_chart(self, data):
        self.figure.clear()
        
        # Create price subplot
        ax1 = self.figure.add_subplot(211)
        ax1.plot(data.index, data['Close'], label='Close Price', color='blue', linewidth=1.5)
        sma_20, _, _, _, bollinger_upper, bollinger_lower = self.calculate_indicators(data)
        ax1.plot(data.index, sma_20, label='SMA (20)', color='orange', linestyle='--', alpha=0.7)
        ax1.plot(data.index, bollinger_upper, label='Bollinger Upper', color='green', linestyle=':', alpha=0.5)
        ax1.plot(data.index, bollinger_lower, label='Bollinger Lower', color='red', linestyle=':', alpha=0.5)
        ax1.fill_between(data.index, bollinger_upper, bollinger_lower, alpha=0.1, color='gray')
        ax1.set_title('Stock Price with Bollinger Bands')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        
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
            
        sma_20, rsi, macd, signal, bollinger_upper, bollinger_lower = self.calculate_indicators(data)
        
        current_price = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2]
        price_change = ((current_price - prev_close) / prev_close) * 100
        
        # Format indicators text
        indicators_text = f"""Current Price: ₹{current_price:.2f} ({price_change:+.2f}%)

"""
        indicators_text += f"SMA (20): ₹{sma_20.iloc[-1]:.2f}"
        indicators_text += f"\nBollinger Bands:"
        indicators_text += f"\n  Upper: ₹{bollinger_upper.iloc[-1]:.2f}"
        indicators_text += f"\n  Lower: ₹{bollinger_lower.iloc[-1]:.2f}"
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