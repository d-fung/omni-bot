from discord.ext import commands
from discord import app_commands
import discord
from utils.lines import get_lines
from utils.injuries import get_injuries

SPORTS_LIST = ['nfl', 'nba', 'mlb']
SPORTS_TITLES = {
    'nfl': {'lines': "NFL Lines", 'injuries': "NFL Injuries"},
    'mlb': {'lines': "MLB Lines", 'injuries': "MLB Injuries"},
    'nba': {'lines': "NBA Lines", 'injuries': "NBA Injuries"}
}
EMBED_COLOR = 0x9CAFBE

class Sports(commands.Cog):

    async def _send_sport_data(self, interaction, sport: str, data_type: str, fetch_func):
        """Helper method to reduce duplication"""
        await interaction.response.defer()

        if sport not in SPORTS_LIST:
            await interaction.followup.send(f"Invalid sport. Choose from: {', '.join(SPORTS_LIST)}")
            return

        title = SPORTS_TITLES[sport][data_type]
        response_list = fetch_func(sport)
        
        for response in response_list:
            embed = discord.Embed(title=title, description=str(response), color=EMBED_COLOR)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name='lines')
    async def lines(self, interaction: discord.Interaction, sport: str):
        await self._send_sport_data(interaction, sport, 'lines', get_lines)
    
    @app_commands.command(name='injuries')
    async def injuries(self, interaction: discord.Interaction, sport: str):
        await self._send_sport_data(interaction, sport, 'injuries', get_injuries)
    
    @lines.autocomplete('sport')
    async def lines_autocomplete(self, interaction: discord.Interaction, current: str):
        data = []
        for sport_choice in ['nfl', 'nba', 'mlb']:
            if current.lower() in sport_choice.lower():
                data.append(app_commands.Choice(name=sport_choice, value=sport_choice))
        return data
    
    @injuries.autocomplete('sport')
    async def injuries_autocomplete(self, interaction: discord.Interaction, current: str):
        data = []
        for sport_choice in ['nfl', 'nba', 'mlb']:
            if current.lower() in sport_choice.lower():
                data.append(app_commands.Choice(name=sport_choice, value=sport_choice))
        return data

async def setup(bot):
    await bot.add_cog(Sports(bot))