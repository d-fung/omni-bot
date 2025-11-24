import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import discord
from datetime import datetime, time
import pytz
import pandas as pd

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
            prepost = True
        else:
            interval = "1d"
            prepost = False
        
        hist = stock.history(period=period, interval=interval, prepost=prepost)
        if period == "1d":
            if hist.index.tz is None:
                hist.index = hist.index.tz_localize('UTC')
        eastern = pytz.timezone("US/Eastern")
        hist.index = hist.index.tz_convert(eastern).tz_localize(None)
        
        # print(hist.index)

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
        
        else:
            # plot multi day charts and fill
            ax.plot(hist.index, hist['Close'], linewidth=2.5, color=line_color, label='Close Price')
            # multi-day charts: normal fill
            ax.fill_between(
                hist.index,
                hist["Close"],
                alpha=0.3,
                color=line_color
            )

        prev_close = stock.info.get("previousClose")

        # plot prev close line only if period = 1d and adjust the boundaries
        if prev_close is not None and period == "1d":
            ax.axhline(prev_close, color="white", alpha=0.7, linestyle="--", linewidth=1.5)
            ax.annotate(
                f'Prev Close:\n${prev_close:.2f}',
                xy=(hist.index[-1], prev_close),
                xytext=(10, 10),  # same offset as current price
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

        # formatting
        ax.set_title(f'{ticker.upper()} Stock Price - {period.upper()}', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (USD)', fontsize=12)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        # format x-axis dates
        if period == "1d":
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

            # change x-axis label to current date for 1d
            current_date = datetime.now(pytz.timezone("US/Eastern")).strftime("%b %d")
            ax.set_xlabel(current_date, fontsize=12)

            # extend x-axis to 8pm even if theres no data yet
            # get current date from data
            trading_day = hist.index[-1].date()
            # create 8pm timestamp for that date

            forced_end = eastern.localize(datetime.combine(trading_day, time(20, 0)))
            forced_end = forced_end.replace(tzinfo=None)
            ax.set_xlim(hist.index[0], forced_end)

        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
            ax.set_xlim(hist.index[0], hist.index[-1])

        ax.margins(x=0)
        plt.xticks(rotation=45)
        
        # add current price annotation
        current_price = hist['Close'].iloc[-1]
        current_time = hist.index[-1].time()

        market_open = time(9, 30)
        market_close = time(16, 0)

        if period == "1d":
            if current_time < market_open:
                box_color = "#888888"
                label_text = f'Premarket:\n${current_price:.2f}'
            elif current_time >= market_close:
                box_color = "#888888"
                label_text = f'After hours:\n${current_price:.2f}'
            else:
                box_color = line_color
                label_text = f'${current_price:.2f}'
        else:
            box_color = line_color
            label_text = f'${current_price:.2f}'

        ax.annotate(label_text, 
                xy=(hist.index[-1], current_price),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc=box_color, alpha=0.7),
                fontsize=12, fontweight='bold')
        
    
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
        hist = stock.history(period=period)
        
        if hist.empty:
            return None
        

        current_price = hist['Close'].iloc[-1]

        # Determine starting price for change calculation
        if period == "1d":
            # For 1d, use previous close
            prev_close = info.get('previousClose', current_price)
        else:
            # For multi-day periods, use first closing price in the period
            prev_close = hist['Close'].iloc[0]
                
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
        
        return {
            'name': info.get('longName', ticker.upper()),
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'volume': info.get('volume', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'high_52w': info.get('fiftyTwoWeekHigh', 'N/A'),
            'low_52w': info.get('fiftyTwoWeekLow', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'open_price': hist['Open'].iloc[-1]
        }
        
    except Exception as e:
        print(f"Error getting stock info for {ticker}: {e}")
        return None