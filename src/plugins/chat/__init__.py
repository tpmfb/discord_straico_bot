from .commands import ChatPlugin

async def setup(bot, config):
    return ChatPlugin(bot, config)