from discord.ext import commands
from typing import List
from plugins.base import BasePlugin


class ChatPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "chat"

    @property
    def description(self) -> str:
        return "Chat commands for AI conversation"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def setup(self) -> None:
        pass

    def get_commands(self) -> List[commands.Command]:
        # Return empty list since we use decorators instead
        return []

    @commands.command(name='chat')
    async def chat(self, ctx, *, message: str):
        user_model = self.config.user_models.get(ctx.author.id, self.config.default_chat_model)

        self.bot.conversation_history.add_message(
            ctx.channel.id,
            "user",
            message,
            ctx.author.display_name
        )

        async with ctx.typing():
            try:
                history = self.bot.conversation_history.get_history(ctx.channel.id)
                # Use persistent session for faster responses
                response = await self.bot.straico_service.chat_completion(
                    model=user_model,
                    messages=history,
                    max_tokens=1000
                )

                ai_response = self._extract_ai_response(response)

                if not ai_response:
                    ai_response = 'Sorry, I could not generate a response.'

                self.bot.conversation_history.add_message(
                    ctx.channel.id,
                    "assistant",
                    ai_response
                )

                await self.bot._send_long_message(ctx.channel, ai_response)

            except Exception as e:
                await ctx.send(f"Error: {str(e)}")

    def _extract_ai_response(self, response):
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