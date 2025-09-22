#!/usr/bin/env python3
"""
Straico Discord Bot - Modular Architecture
Main entry point for the bot application.
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.bot import StraicoBot
from core.config import Config
from core.logger import setup_logger
from core.errors import ConfigurationError


async def main():
    try:
        config = Config.from_env()
        config.validate()
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    logger = setup_logger("straico_bot", config.log_level, config.log_file)
    logger.info("Starting Straico Discord Bot...")

    bot = StraicoBot(config)

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(bot.close())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await bot.start(config.discord_token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
    finally:
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)