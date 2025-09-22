from .commands import UtilityPlugin

async def setup(bot, config):
    return UtilityPlugin(bot, config)