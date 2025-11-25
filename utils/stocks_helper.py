import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import discord
from datetime import datetime, time
import pytz
import pandas as pd
import numpy as np

def create_stock_chart(ticker: str, period: str = "1d"):
    """
    Create a stock chart and return as Discord file
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y)
    
    Returns:
        discord.File object or None if error
    """
    try:
        stock = yf.Ticker(ticker)
        
        # valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 4h, 1d, 5d, 1wk, 1mo, 3mo
        if period == "1d":
            interval = "5m"
            prepost = True
        elif period == "5d":
            interval = "30m"
            prepost = False
        else:
            interval = "1d"
            prepost = False
        
        hist = stock.history(period=period, interval=interval, prepost=prepost, auto_adjust=False)
        if period == "1d":
            if hist.index.tz is None:
                hist.index = hist.index.tz_localize('UTC')
        eastern = pytz.timezone("US/Eastern")
        hist.index = hist.index.tz_convert(eastern).tz_localize(None)
        

        # for timestamp, row in hist.iterrows():
        #     print(timestamp, row["Close"])

        
        if hist.empty:
            return None
        
        # determine color based on performance
        price_change = hist['Close'].iloc[-1] - hist['Close'].iloc[0]
        line_color = '#00ff00' if price_change >= 0 else '#ff0000'
        
        # create the chart with dark theme
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if period == "1d":
            premarket = hist.between_time("00:00", "09:30")
            regular_hours = hist.between_time("09:30", "16:00")  # NYSE regular
            postmarket = hist.between_time("16:00", "23:59")
           
            # plot premarket
            if not premarket.empty:
                ax.plot(premarket.index, premarket['Close'], color="#888888",
                        linestyle="--", linewidth=1.5)            
                ax.fill_between(
                    premarket.index,
                    premarket["Close"],
                    alpha=0.2,
                    color="#888888"
                )  
            # plot regular hours
            if not regular_hours.empty:
                ax.plot(regular_hours.index, regular_hours['Close'], color=line_color, linewidth=2.5)
                # fill regular hours area
                ax.fill_between(
                    regular_hours.index,
                    regular_hours["Close"],
                    alpha=0.3,
                    color=line_color
                )

            # plot after hours in gray
            if not postmarket.empty:
                ax.plot(postmarket.index, postmarket['Close'], color="#888888", linewidth=1.5, linestyle='--')
                ax.fill_between(
                    postmarket.index,
                    postmarket["Close"],
                    alpha=0.2,
                    color="#888888"
                )
            
            prev_close = stock.info.get("previousClose")

            # plot prev close line and adjust boundaries
            if prev_close is not None:
                ax.axhline(prev_close, color="white", alpha=0.7, linestyle="--", linewidth=1.5)
                ax.annotate(
                    f'Prev Close:\n${prev_close:.2f}',
                    xy=(hist.index[-1], prev_close),
                    xytext=(10, 10),
                    textcoords='offset points',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#2C2F33", alpha=0.7),
                    color="white",
                    fontsize=12,
                    fontweight='bold'
                )

                ymin = min(hist['Close'].min(), prev_close)
                ymax = max(hist['Close'].max(), prev_close)    
            else:
                ymin = hist['Close'].min()
                ymax = hist['Close'].max()

            padding = (ymax - ymin) * 0.05  # 5% margin
            ax.set_ylim(ymin - padding, ymax + padding)
            
            # format x-axis for 1d
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            current_date = datetime.now(pytz.timezone("US/Eastern")).strftime("%b %d")
            ax.set_xlabel(current_date, fontsize=12)

            # extend x-axis to 8pm even if theres no data yet
            trading_day = hist.index[-1].date()
            forced_end = eastern.localize(datetime.combine(trading_day, time(20, 0)))
            forced_end = forced_end.replace(tzinfo=None)
            
            ax.set_xlim(hist.index[0], forced_end)
            ax.margins(x=0)
            
            # add current price annotation with color based on market hours
            current_price = hist['Close'].iloc[-1]
            current_time = hist.index[-1].time()
            market_open = time(9, 30)
            market_close = time(16, 0)

            if current_time < market_open:
                box_color = "#888888"
                label_text = f'${current_price:.2f}\n(Pre-Market)'
            elif current_time >= market_close:
                box_color = "#888888"
                label_text = f'${current_price:.2f}\n(After-Hours)'
            else:
                box_color = line_color
                label_text = f'${current_price:.2f}'

            ax.annotate(label_text, 
                       xy=(hist.index[-1], current_price),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.5', fc=box_color, alpha=0.7),
                       fontsize=12, fontweight='bold')
        
        else:
            # For multi-day: remove gaps by using integer index
            actual_dates = hist.index.copy()
            hist_plot = hist.reset_index(drop=True)
            
            # plot with integer index (no gaps)
            ax.plot(hist_plot.index, hist_plot['Close'], linewidth=2.5, color=line_color)
            ax.fill_between(hist_plot.index, hist_plot["Close"], alpha=0.3, color=line_color)
            
            prev_close = stock.info.get("previousClose")
            
            if prev_close is not None:
                ymin = min(hist_plot['Close'].min(), prev_close)
                ymax = max(hist_plot['Close'].max(), prev_close)    
            else:
                ymin = hist_plot['Close'].min()
                ymax = hist_plot['Close'].max()

            padding = (ymax - ymin) * 0.05
            ax.set_ylim(ymin - padding, ymax + padding)
            
            # Set x-axis to show actual dates at intervals
            num_ticks = min(8, len(hist_plot))
            tick_positions = np.linspace(0, len(hist_plot)-1, num_ticks, dtype=int)
            ax.set_xticks(tick_positions)
            ax.set_xticklabels([actual_dates[i].strftime("%b %d") for i in tick_positions])
            
            ax.set_xlim(0, len(hist_plot)-1)
            ax.margins(x=0)
            
            # Add current price annotation (using integer position)
            current_price = hist_plot['Close'].iloc[-1]
            ax.annotate(f'${current_price:.2f}', 
                       xy=(hist_plot.index[-1], current_price),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.5', fc=line_color, alpha=0.7),
                       fontsize=12, fontweight='bold')

        # Common formatting
        ax.set_title(f'{ticker.upper()} Stock Price - {period.upper()}', fontsize=18, fontweight='bold', pad=20)
        ax.set_ylabel('Price (USD)', fontsize=12)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='#2C2F33')
        buf.seek(0)
        plt.close(fig)
        
        # return as Discord file
        return discord.File(buf, filename=f'{ticker}_chart.png')
        
    except Exception as e:
        print(f"Error creating chart for {ticker}: {e}")
        return None

def get_stock_info(ticker: str, period: str = "1d"):
    """
    Get stock information from yfinance
    
    Args:
        ticker: stock symbol
        period: time period (1d, 5d, 1mo, etc.)
    
    Returns:
        dict with stock info or None if error
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # for some reason Google's 5d chart uses the open value of the very first candle at 9:30 
        # instead of close of the first day
        # the logic below is needed to replicate that behaviour

        hist = stock.history(period=period, auto_adjust=False, interval="1d")

        # for timestamp, row in hist.iterrows():
        #     print(timestamp, row["Close"])
        #print(hist.iloc[0])

        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        # Determine starting price for change calculation
        if period == "1d":
            # For 1d, use previous close
            prev_close = info.get('previousClose', current_price)
        
        elif period == "5d":
            # Google uses this to calculate prev_close
            hist = stock.history(period=period, auto_adjust=False, interval="30m")
            prev_close = hist['Open'].iloc[0]

        else:
            # For multi-day periods, use first closing price in the period
            prev_close = hist['Close'].iloc[0]
                
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

        result = {
            'name': info.get('longName', ticker.upper()),
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'volume': info.get('volume', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'high_52w': info.get('fiftyTwoWeekHigh', 'N/A'),
            'low_52w': info.get('fiftyTwoWeekLow', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'open_price': open_price
        }
    
            # additional info if in pre/post market
        eastern = pytz.timezone('US/Eastern')
        current_time = datetime.now(eastern).time()
        premarket_open = time(4,0)
        market_open = time(9, 30)
        market_close = time(16, 0)

        if current_time < market_open or current_time >= market_close:
            prepost_hist = stock.history(period="1d", auto_adjust=False, interval="5m", prepost=True)
            prepost_close = prepost_hist['Close'].iloc[-1]
            prepost_change = prepost_close - current_price
            prepost_change_pct = (prepost_change / current_price) * 100 if current_price != 0 else 0
            prepost_label = "Premarket" if premarket_open < current_time and current_time < market_open else "After hours"

            # add prepost data to result
            result['prepost_label'] = prepost_label
            result['prepost_close'] = prepost_close
            result['prepost_change'] = prepost_change
            result['prepost_change_pct'] = prepost_change_pct

        return result
        
    except Exception as e:
        print(f"Error getting stock info for {ticker}: {e}")
        return None