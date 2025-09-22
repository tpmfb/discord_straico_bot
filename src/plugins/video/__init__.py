from .commands import VideoPlugin

async def setup(bot, config):
    return VideoPlugin(bot, config)