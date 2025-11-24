from dotenv import load_dotenv
from discord import Intents, Message
from discord.ext import commands
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')
    
    # load all cogs
    await bot.load_extension('cogs.sports')
    await bot.load_extension('cogs.llm')
    await bot.load_extension('cogs.general')

    await bot.tree.sync()
    print('Commands synced!')

@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    
    await bot.process_commands(message)

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()