# cogs/general.py
from discord.ext import commands
from discord import app_commands
import discord
import datetime

class General(commands.Cog):
    # general bot commands and utilities
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='help', description='Show all available commands')
    async def help(self, interaction: discord.Interaction):
        # display all bot commands
        embed = discord.Embed(
            title="🤖 Omni Bot - Command List",
            description="Here are all available commands:",
            color=0x00ff00
        )
        
        # sports commands
        embed.add_field(
            name="🏈 Sports Commands",
            value=(
                "`/lines <sport>` - Get betting lines (nfl, nba, mlb)\n"
                "`/injuries <sport>` - Get injury reports (nfl, nba, mlb)"
            ),
            inline=False
        )
        
        # AI commands
        embed.add_field(
            name="🤖 AI Commands",
            value="`/ask <query>` - Ask the AI anything",
            inline=False
        )
        
        # general commands
        embed.add_field(
            name="⚙️ General Commands",
            value=(
                "`/help` - Show this message\n"
                "`/ping` - Check bot latency\n"
                "`/info` - Show bot information\n"
                "`/serverinfo` - Show server information"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use / to see all commands with autocomplete")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='ping', description='Check bot latency')
    async def ping(self, interaction: discord.Interaction):
        # checks bot's response time
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=0x00ff00 if latency < 100 else 0xffff00 if latency < 200 else 0xff0000
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='info', description='Show bot information')
    async def info(self, interaction: discord.Interaction):
        # display information about the bot
        embed = discord.Embed(
            title="ℹ️ Bot Information",
            description="Omni Bot - Your all-in-one Discord assistant",
            color=0x3498db
        )
        
        embed.add_field(name="👥 Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="👤 Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="📊 Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        embed.add_field(
            name="✨ Features",
            value="• Sports betting lines\n• Injury reports\n• AI chat assistant",
            inline=False
        )
        
        embed.set_footer(text=f"Running on discord.py {discord.__version__}")
        embed.timestamp = datetime.datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='serverinfo', description='Show server information')
    async def serverinfo(self, interaction: discord.Interaction):
        # display information about the current server
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            description="Server Information",
            color=0x9b59b6
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="👥 Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="💬 Channels", value=str(len(guild.channels)), inline=True)
        
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="🎭 Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="😀 Emojis", value=str(len(guild.emojis)), inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))