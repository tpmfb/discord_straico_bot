# Migration Guide: Modular Discord Bot Architecture

## Overview

Your Discord bot has been successfully refactored from a monolithic structure to a modular, plugin-based architecture. This guide explains the changes and how to use the new system.

## Before vs After

### Before (Monolithic)
```
discord_straico_bot_v2/
├── bot.py (774 lines - all functionality)
├── straico_client.py
├── STRAICO_MODELS.py
├── STRAICO_IMAGE_MODELS.py
└── requirements.txt
```

### After (Modular)
```
src/
├── core/           # Core bot framework
├── plugins/        # Modular command plugins
├── services/       # Business logic services
├── utils/          # Utility functions
├── config/         # Configuration files
└── main.py         # Entry point
```

## Key Improvements

1. **Modular Architecture**: Commands organized into logical plugins
2. **Plugin System**: Easy to add new features without touching core code
3. **Separation of Concerns**: Clear boundaries between different responsibilities
4. **Better Error Handling**: Centralized error management
5. **Configuration Management**: Centralized settings
6. **Improved Maintainability**: Smaller, focused files

## Running the New Bot

### Option 1: Use the new modular version
```bash
cd src
python main.py
```

### Option 2: Keep using the old version
Your original `bot.py` still works as before:
```bash
python bot.py
```

## Directory Structure Explained

### `src/core/`
- `bot.py`: Main bot class with plugin loading
- `config.py`: Configuration management
- `errors.py`: Custom exception classes
- `logger.py`: Logging setup

### `src/plugins/`
- `chat/`: Chat completion commands
- `image/`: Image generation commands
- `video/`: Video generation commands
- `utility/`: Utility commands (help, models, etc.)

### `src/services/`
- `straico.py`: Straico API client
- `conversation.py`: Conversation history management

### `src/utils/`
- `validators.py`: Input validation functions
- `formatters.py`: Message formatting utilities

### `src/config/`
- `models.py`: Available AI models
- `settings.py`: Default configuration

## Adding New Commands

### Creating a New Plugin

1. Create a new directory in `src/plugins/`:
```bash
mkdir src/plugins/music
```

2. Create the plugin files:
```python
# src/plugins/music/__init__.py
from .commands import MusicPlugin

async def setup(bot, config):
    return MusicPlugin(bot, config)
```

```python
# src/plugins/music/commands.py
from discord.ext import commands
from typing import List
from ..base import BasePlugin

class MusicPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "music"

    @property
    def description(self) -> str:
        return "Music playback commands"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def setup(self) -> None:
        pass

    def get_commands(self) -> List[commands.Command]:
        return [
            commands.Command(self.play, name='play'),
            commands.Command(self.stop, name='stop'),
        ]

    async def play(self, ctx, *, song: str):
        # Your music logic here
        await ctx.send(f"Playing: {song}")

    async def stop(self, ctx):
        # Your stop logic here
        await ctx.send("Music stopped")
```

The plugin will be automatically loaded when the bot starts!

## Configuration

Environment variables remain the same:
- `DISCORD_TOKEN`
- `STRAICO_API_KEY`
- `COMMAND_PREFIX` (optional, defaults to "!")

## Benefits of the New Architecture

1. **Scalability**: Easy to add new features
2. **Maintainability**: Smaller, focused files
3. **Testability**: Individual components can be tested
4. **Reusability**: Plugins can be shared between projects
5. **Team Development**: Multiple developers can work on different plugins

## Backwards Compatibility

- All existing commands work the same way
- Environment variables unchanged
- Bot behavior is identical to users

## Next Steps

1. Install dependencies: `pip install -r requirements-new.txt`
2. Test the new bot: `cd src && python main.py`
3. Add new features as plugins in the `src/plugins/` directory
4. Enjoy the improved architecture!

## Need Help?

- Check the plugin examples in `src/plugins/`
- Look at the base plugin class in `src/plugins/base.py`
- Each plugin is self-contained and easy to understand