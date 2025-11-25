# 🤖 Omni Bot

An all-in-one Discord bot that provides sports statistics, injury reports, betting lines, and AI-powered chat assistance.

📸 Screenshots
### Bot Commands in Action
<img width="350" height="350" alt="Image" src="https://github.com/user-attachments/assets/cc48451b-9be9-4b7d-94e5-1383e670be1f" />

### Stock Market Prices

<img width="350" height="350" alt="Image" src="https://github.com/user-attachments/assets/de5bd048-e4f5-4b1e-8a61-a6349b2d0bba" />

### Sports Betting Lines
<img width="350" height="350" alt="Image" src="https://github.com/user-attachments/assets/dd4fea42-9548-41ec-ad28-a35761fdd7b8" />

### AI Chat Response
<img width="599" height="221" alt="Image" src="https://github.com/user-attachments/assets/d17491c0-0c13-4311-b57f-89bf53d09d95" />



## ✨ Features

### 🏈 Sports Commands
- **Betting Lines** - Get real-time betting lines for NFL, NBA, and MLB
- **Injury Reports** - Track player injuries across major sports leagues
- Multi-sport support with easy-to-read embed formatting

### 📊 Stock Market
- **Real-time Stock Data** - Get current stock prices, charts, and key metrics
- **Interactive Charts** - Visual price charts with pre-market and after-hours data
- **Multiple Timeframes** - View 1-day, 5-day, 1-month, 3-month, 6-month, 1-year, and 5-year charts
- **Extended Hours Trading** - Track pre-market and after-hours price movements

### 🤖 AI Assistant
- **AI Chat** - Ask questions and get intelligent responses powered by DeepSeek AI
- Natural language processing for conversational interactions

### ⚙️ General Utilities
- **Bot Information** - View bot stats and features
- **Server Information** - Get details about your Discord server
- **Latency Check** - Monitor bot performance
- **Help Command** - Easy-to-navigate command reference

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Discord Bot Token
- DeepSeek API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/omni-bot.git
   cd omni-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   TOKEN=your_discord_bot_token
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## 📋 Commands

All commands use Discord's slash command interface. Type `/` in Discord to see the full list.

### Sports Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/lines` | Get betting lines | `/lines sport:nba` |
| `/injuries` | Get injury reports | `/injuries sport:nfl` |

**Supported Sports:** NFL, NBA, MLB

### Stock Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/stock` | Get stock information and chart | `/stock ticker:AAPL period:1m` |

**Supported Periods:** 1d, 5d, 1m, 3m, 6m, 1y, 5y

### AI Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/ask` | Ask AI a question | `/ask query:What's the weather?` |

### General Commands
| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/ping` | Check bot latency |
| `/info` | Display bot information |
| `/serverinfo` | Show server details |

## 🏗️ Project Structure

```
omni-bot/
├── cogs/
│   ├── __init__.py
│   ├── general.py      # General utility commands
│   ├── llm.py          # AI chat functionality
│   ├── sports.py       # Sports statistics & betting
│   └── stocks.py       # Stock market data & charts
├── utils/
│   ├── __init__.py
│   ├── ai_helper.py    # AI response handling
│   ├── helper_functions.py
│   ├── injuries.py     # Injury data fetching
│   ├── lines.py        # Betting lines fetching
│   └── stock_helpers.py # Stock data & chart generation
├── .env                # Environment variables (not tracked)
├── .gitignore
├── main.py             # Bot entry point
├── requirements.txt
└── README.md
```

## 🛠️ Tech Stack

- **Discord.py** - Discord bot framework
- **yfinance** - Real-time stock market data
- **matplotlib** - Chart generation and visualization
- **OpenAI SDK** - AI integration (DeepSeek)
- **Python-dotenv** - Environment variable management

## 🔧 Configuration

### Bot Permissions Required
- Read Messages
- Send Messages
- Embed Links
- Use Slash Commands

### Intents Required
- Message Content Intent (for logging)

## 📝 Development

### Adding New Commands

Commands are organized into cogs for modularity:

1. Navigate to the appropriate cog file in `cogs/`
2. Add your command using the `@app_commands.command()` decorator
3. The command will automatically sync on bot startup

Example:
```python
@app_commands.command(name='example', description='An example command')
async def example(self, interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")
```

### Adding New Utilities

Create new utility functions in the `utils/` folder and import them into the relevant cog.
