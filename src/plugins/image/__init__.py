from .commands import ImagePlugin

async def setup(bot, config):
    return ImagePlugin(bot, config)