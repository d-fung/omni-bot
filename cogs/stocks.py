# cogs/stocks.py
from discord.ext import commands
from discord import app_commands
import discord
from utils.stocks_helper import create_stock_chart, get_stock_info

class Stocks(commands.Cog):
    # stock market information and charts
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='stock', description='Get stock information and chart')
    @app_commands.describe(
        ticker='Stock symbol (e.g., AAPL, TSLA, GOOGL)',
        period='Chart time period'
    )
    async def stock(self, interaction: discord.Interaction, ticker: str, period: str = "1d"):
        await interaction.response.defer()
        
        ticker = ticker.upper()

        valid_periods = ["1d", "5d", "1m", "3m", "6m", "1y", "5y"]
        if period not in valid_periods:
            await interaction.followup.send(f"❌ Invalid period. Choose from: {', '.join(valid_periods)}")
            return
        
        # convert m back to mo for months for API use
        # originally set to use "m" for months for user consistency (even though m = minutes)

        if period[1] == "m":
            # add in "o" to make "mo" for months
            period += "o"
        
        
        # get stock info
        stock_data = get_stock_info(ticker, period)
        
        if not stock_data:
            await interaction.followup.send(f"❌ Could not find data for ticker: **{ticker}**")
            return
        
        # create embed
        color = 0x00ff00 if stock_data['change'] >= 0 else 0xff0000
        # set positive or negative change theme
        if stock_data['change'] >= 0:
            color = 0x00ff00
            arrow_icon = "⬆️"
        else:
            color = 0xff0000
            arrow_icon = "⬇️"

        period_to_text = {
            "1d" : "today",
            "5d" : "past 5 days",
            "1mo" : "past month",
            "3mo" : "past 3 months",
            "6mo" : "past 6 months",
            "1y" : "past year",
            "5y" : "past 5 years"
        }

        description = ""
        # adds prepost data if exists
        if 'prepost_label' in stock_data:
            change_emoji = "🟢" if stock_data['prepost_change'] >= 0 else "🔴"
            description = f"`{change_emoji} {stock_data['prepost_label']}: ${stock_data['prepost_close']:.2f} {stock_data['prepost_change']:+.2f} ({stock_data['prepost_change_pct']:+.2f}%)`"


        embed = discord.Embed(
            title=f"📈 {ticker} - {stock_data['name']}\n${stock_data['current_price']:.2f}\n{stock_data['change']:+.2f} ({stock_data['change_pct']:+.2f}%) {arrow_icon} {period_to_text[period]}",
            description=description,
            color=color
        )
        
        embed.add_field(
            name="📂 Open",
            value=f"${stock_data['open_price']:.2f}" if isinstance(stock_data['open_price'], (float, int)) else "N/A",
            inline=True
        )

        embed.add_field(
            name="📈 52W High", 
            value=f"${stock_data['high_52w']:.2f}" if isinstance(stock_data['high_52w'], float) else "N/A", 
            inline=True
        )

        if isinstance(stock_data['market_cap'], int):
            market_cap_str = f"${stock_data['market_cap'] / 1e9:.2f}B"
        else:
            market_cap_str = "N/A"
            
        embed.add_field(
            name="💼 Market Cap", 
            value=market_cap_str, 
            inline=True
        )
        
        embed.add_field(
            name="📦 Volume", 
            value=f"{stock_data['volume']:,}" if isinstance(stock_data['volume'], int) else "N/A", 
            inline=True
        )

        embed.add_field(
            name="📉 52W Low", 
            value=f"${stock_data['low_52w']:.2f}" if isinstance(stock_data['low_52w'], float) else "N/A", 
            inline=True
        )
        
        embed.add_field(
            name="📊 P/E Ratio",
            value=f"{stock_data['pe_ratio']:.2f}" if isinstance(stock_data['pe_ratio'], (float, int)) else "N/A",
            inline=True
        )
        
        # create chart
        chart_file = create_stock_chart(ticker, period)
        
        if chart_file:
            embed.set_image(url=f"attachment://{ticker}_chart.png")
            await interaction.followup.send(embed=embed, file=chart_file)
        else:
            await interaction.followup.send(embed=embed)
    
    @stock.autocomplete('period')
    async def period_autocomplete(self, interaction: discord.Interaction, current: str):
        periods = [
            ('1d', '1d'),
            ('5d', '5d'),
            ('1m', '1m'),
            ('3m', '3m'),
            ('6m', '6m'),
            ('1y', '1y'),
            ('5y', '5y')
        ]
        return [
            app_commands.Choice(name=name, value=value)
            for name, value in periods
            if current.lower() in name.lower() or current.lower() in value.lower()
        ]

async def setup(bot):
    await bot.add_cog(Stocks(bot))