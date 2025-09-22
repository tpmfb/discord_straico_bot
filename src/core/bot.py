import discord
from discord.ext import commands
import importlib
import pkgutil
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

from .config import Config
from .errors import PluginError
from plugins.base import BasePlugin
from services.straico import StraicoService
from services.conversation import ConversationHistory


class StraicoBot(commands.Bot):
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=config.command_prefix,
            intents=intents,
            help_command=None
        )

        self.config = config
        self.plugins: Dict[str, BasePlugin] = {}
        self.straico_service = None
        self.conversation_history = ConversationHistory(config.max_history_per_channel)
        self.logger = logging.getLogger(__name__)

    async def setup_hook(self):
        # Create a persistent Straico service session
        self.straico_service = StraicoService(
            api_key=self.config.straico_api_key,
            base_url=self.config.api_base_url
        )
        # Initialize the session immediately for performance
        await self.straico_service.__aenter__()

        await self.load_plugins()

    async def on_ready(self):
        self.logger.info(f'{self.user} has connected to Discord!')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        self.logger.info(f'Loaded {len(self.plugins)} plugins')

    async def load_plugins(self):
        plugins_path = Path(__file__).parent.parent / 'plugins'

        for finder, name, ispkg in pkgutil.iter_modules([str(plugins_path)]):
            if name == 'base' or name.startswith('_'):
                continue

            try:
                module = importlib.import_module(f'plugins.{name}')
                if hasattr(module, 'setup'):
                    plugin = await module.setup(self, self.config)
                    if isinstance(plugin, BasePlugin):
                        await self.register_plugin(plugin)
                        self.logger.info(f"Loaded plugin: {plugin.name}")
                    else:
                        self.logger.warning(f"Plugin {name} setup() did not return a BasePlugin instance")
                else:
                    self.logger.warning(f"Plugin {name} has no setup() function")

            except Exception as e:
                self.logger.error(f"Failed to load plugin {name}: {e}")

    async def register_plugin(self, plugin: BasePlugin):
        if plugin.name in self.plugins:
            raise PluginError(f"Plugin {plugin.name} is already registered")

        try:
            await plugin.setup()

            # Add the plugin as a cog
            await self.add_cog(plugin)

            # Also register any manual commands and listeners
            for command in plugin.get_commands():
                self.add_command(command)

            for event_name, handler in plugin.get_listeners():
                self.add_listener(handler, event_name)

            self.plugins[plugin.name] = plugin

        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin.name}: {e}")
            raise PluginError(f"Failed to register plugin {plugin.name}: {e}")

    async def unload_plugin(self, plugin_name: str):
        if plugin_name not in self.plugins:
            raise PluginError(f"Plugin {plugin_name} is not loaded")

        plugin = self.plugins[plugin_name]

        try:
            await plugin.teardown()

            for command in plugin.get_commands():
                self.remove_command(command.name)

            for event_name, handler in plugin.get_listeners():
                self.remove_listener(handler, event_name)

            del self.plugins[plugin_name]
            self.logger.info(f"Unloaded plugin: {plugin_name}")

        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            raise PluginError(f"Failed to unload plugin {plugin_name}: {e}")

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)

        if (message.channel.id in self.config.auto_response_channels and
            not message.content.startswith(self.command_prefix)):

            self.conversation_history.add_message(
                message.channel.id,
                "user",
                message.content,
                message.author.display_name
            )

            async with message.channel.typing():
                try:
                    await self._generate_auto_response(message)
                except Exception as e:
                    self.logger.error(f"Error in auto-response: {e}")

    async def _generate_auto_response(self, message):
        history = self.conversation_history.get_history(message.channel.id)

        try:
            # Use persistent session for better performance
            response = await self.straico_service.chat_completion(
                model=self.config.default_chat_model,
                messages=history,
                max_tokens=1500
            )

            ai_response = self._extract_ai_response(response)

            if ai_response:
                self.conversation_history.add_message(
                    message.channel.id,
                    "assistant",
                    ai_response
                )
                await self._send_long_message(message.channel, ai_response)
            else:
                await message.channel.send('Sorry, I could not generate a response.')

        except Exception as e:
            await self._handle_api_error(message.channel, e)

    def _extract_ai_response(self, response) -> Optional[str]:
        if isinstance(response, dict) and 'data' in response:
            data = response['data']
            if 'completions' in data:
                completions = data['completions']
                for model_key, model_data in completions.items():
                    if 'completion' in model_data:
                        completion = model_data['completion']
                        if 'choices' in completion and completion['choices']:
                            choice = completion['choices'][0]
                            if 'message' in choice and 'content' in choice['message']:
                                content = choice['message']['content'].strip()
                                if content:
                                    return content
        return None

    async def _handle_api_error(self, channel, error):
        error_msg = str(error)
        if "500" in error_msg:
            await channel.send("🔄 The AI service is temporarily unavailable. Please try again in a moment.")
        elif "422" in error_msg:
            await channel.send("⚠️ There was an issue with the request format. Please try rephrasing your message.")
        else:
            await channel.send(f"❌ Error generating response: {error_msg}")

    async def _send_long_message(self, channel, content: str):
        if len(content) <= self.config.max_message_length:
            await channel.send(content)
        else:
            chunks = []
            current_chunk = ""

            for line in content.split('\n'):
                if len(current_chunk + line + '\n') <= self.config.max_message_length:
                    current_chunk += line + '\n'
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = line + '\n'

            if current_chunk:
                chunks.append(current_chunk.strip())

            for chunk in chunks:
                await channel.send(chunk)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Command not found. Use `!help` to see available commands.")
        else:
            self.logger.error(f"Command error: {error}")

            for plugin in self.plugins.values():
                if await plugin.on_error(ctx, error):
                    return

            await ctx.send(f"❌ An error occurred: {str(error)}")

    async def close(self):
        for plugin in self.plugins.values():
            try:
                await plugin.teardown()
            except Exception as e:
                self.logger.error(f"Error during plugin teardown: {e}")

        # Clean up persistent Straico service session
        if self.straico_service:
            try:
                await self.straico_service.__aexit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error closing Straico service: {e}")

        await super().close()