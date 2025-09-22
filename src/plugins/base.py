from abc import ABCMeta, abstractmethod
from typing import Dict, List, Any, Optional
import discord
from discord.ext import commands
import logging

class CogABCMeta(ABCMeta, type(commands.Cog)):
    pass

class BasePlugin(commands.Cog, metaclass=CogABCMeta):
    def __init__(self, bot: commands.Bot, config: Any):
        self.bot = bot
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    async def setup(self) -> None:
        pass

    async def teardown(self) -> None:
        pass

    def get_commands(self) -> List[commands.Command]:
        return []

    def get_listeners(self) -> List[tuple]:
        return []

    async def on_error(self, ctx: commands.Context, error: Exception) -> bool:
        return False