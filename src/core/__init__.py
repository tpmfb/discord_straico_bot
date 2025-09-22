# Core module - import on demand to avoid dependency issues
from .errors import BotError, APIError, ValidationError
from .logger import setup_logger

__all__ = ['StraicoBot', 'Config', 'BotError', 'APIError', 'ValidationError', 'setup_logger']

def get_bot():
    from .bot import StraicoBot
    return StraicoBot

def get_config():
    from .config import Config
    return Config