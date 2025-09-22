# Straico Discord Bot

Discord bot for AI interactions with a modular plugin system.

## Architecture

```
src/
├── 🧠 core/           # Bot framework & configuration
├── 🔌 plugins/        # Modular command plugins
├── ⚙️ services/       # Business logic & API clients
├── 🛠️ utils/          # Utility functions
├── 📋 config/         # Model definitions & settings
└── 🚀 main.py         # Application entry point
```

## Features

- **Modular Plugin System**: Easy to add new commands
- **Chat Completion**: AI conversations with context
- **Image Generation**: Multiple AI image models
- **Video Generation**: AI video creation
- **Auto-Response**: Automatic AI responses in channels
- **Model Selection**: Choose from 90+ AI models
- **Conversation History**: Context-aware conversations

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements-new.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

3. **Run the Bot**
   ```bash
   cd src
   python main.py
   ```

## 🔌 Available Plugins

### Chat Plugin
- `!chat <message>` - AI conversation
- `!setmodel <name>` - Set preferred model
- `!currentmodel` - Show current model

### Image Plugin
- `!image <prompt>` - Quick image generation
- `!genimage` - Step-by-step workflow
- `!imagemodels` - List available models

### Video Plugin (Current not available)
- `!video <prompt>` - Generate videos
- `!status <id>` - Check generation status

### Utility Plugin
- `!help` - Show all commands
- `!models` - List all AI models
- `!userinfo` - Account information
- `!auto` - Toggle auto-response
- `!clear` - Clear conversation history

## 🔧 Adding New Features

### Create a New Plugin

1. **Create Plugin Directory**
   ```bash
   mkdir src/plugins/mynewfeature
   ```

2. **Plugin Setup** (`src/plugins/mynewfeature/__init__.py`)
   ```python
   from .commands import MyNewFeaturePlugin

   async def setup(bot, config):
       return MyNewFeaturePlugin(bot, config)
   ```

3. **Plugin Commands** (`src/plugins/mynewfeature/commands.py`)
   ```python
   from discord.ext import commands
   from typing import List
   from ..base import BasePlugin

   class MyNewFeaturePlugin(BasePlugin):
       @property
       def name(self) -> str:
           return "mynewfeature"

       @property
       def description(self) -> str:
           return "Description of my new feature"

       @property
       def version(self) -> str:
           return "1.0.0"

       async def setup(self) -> None:
           pass

       def get_commands(self) -> List[commands.Command]:
           return [
               commands.Command(self.my_command, name='mycommand'),
           ]

       async def my_command(self, ctx, *, args: str):
           await ctx.send(f"New feature: {args}")
   ```

The plugin is automatically loaded on bot restart!

## Configuration

### Environment Variables
```bash
DISCORD_TOKEN=your_discord_bot_token
STRAICO_API_KEY=your_straico_api_key
COMMAND_PREFIX=!
LOG_LEVEL=INFO
MAX_HISTORY_PER_CHANNEL=100
```

### Plugin Configuration
Each plugin can access the global configuration:
```python
async def my_command(self, ctx):
    max_history = self.config.max_history_per_channel
    default_model = self.config.default_chat_model
```

## Error Handling

### Custom Exceptions
```python
from core.errors import BotError, APIError, ValidationError

try:
    # Some operation
    pass
except APIError as e:
    # Handle API errors
    pass
```

### Plugin Error Handling
```python
async def on_error(self, ctx, error):
    if isinstance(error, MyCustomError):
        await ctx.send("Custom error message")
        return True  # Error handled
    return False  # Let core handle it
```

## 📝 Logging

```python
from core.logger import setup_logger

logger = setup_logger("my_plugin", "INFO")
logger.info("Plugin loaded successfully")
```

## 🧪 Testing

Run architecture tests:
```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from services.conversation import ConversationHistory
from config.models import STRAICO_MODELS
print(f'✅ {len(STRAICO_MODELS)} models loaded')
"
```

## Plugin Examples

See the existing plugins for reference:
- `src/plugins/chat/` - AI conversation handling
- `src/plugins/image/` - Image generation workflow
- `src/plugins/video/` - Video generation
- `src/plugins/utility/` - Bot utilities

## 🤝 Contributing

1. Create a new plugin for your feature
2. Follow the existing plugin patterns
3. Add appropriate error handling
4. Test your plugin independently

## 📄 License

This project structure can be freely adapted for other Discord bot projects.