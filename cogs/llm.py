from discord.ext import commands
from discord import app_commands
import discord
from utils.llm_response import get_response

class LLM(commands.Cog):
    """AI-powered chat and assistance"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='ask', description='Ask the AI a question')
    async def ask(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        response_list = get_response(query)

        print(f"AI Response for '{query}': {response_list}")

        for response in response_list:
            embed = discord.Embed(description=str(response), color=0x4E6BFD)
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LLM(bot))