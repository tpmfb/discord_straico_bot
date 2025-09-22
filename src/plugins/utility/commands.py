import discord
from discord.ext import commands
from typing import List
from plugins.base import BasePlugin
from config.models import STRAICO_MODELS


class UtilityPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "utility"

    @property
    def description(self) -> str:
        return "Utility commands for bot management and information"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def setup(self) -> None:
        pass

    def get_commands(self) -> List[commands.Command]:
        # Return empty list since we use decorators instead
        return []

    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(title="Straico Bot Commands", color=0x00ff00)
        embed.add_field(
            name="Chat Commands",
            value="`!chat <message>` - Chat with AI\n`!setmodel <model_name>` - Set your preferred model\n`!currentmodel` - Show your current model\n`!models` - List available models",
            inline=False
        )
        embed.add_field(
            name="Generation Commands",
            value="`!image <prompt>` - Quick image generation\n`!genimage` - Step-by-step image workflow\n`!cancelimage` - Cancel image workflow\n`!imagemodels` - List image models\n`!video <prompt>` - Generate a video\n`!status <id>` - Check generation status",
            inline=False
        )
        embed.add_field(
            name="Utility Commands",
            value="`!userinfo` - Get your Straico account info\n`!auto` - Toggle auto-response in this channel\n`!clear` - Clear conversation history",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='models')
    async def list_models(self, ctx):
        embed = discord.Embed(title="Available Straico Models", color=0x0099ff)

        chat_models = []
        image_models = []
        video_models = []
        audio_models = []

        for model in STRAICO_MODELS:
            model_lower = model.lower()

            if any(keyword in model_lower for keyword in ['dall-e', 'flux', 'ideogram', 'imagen', 'recraft', 'bagel']):
                image_models.append(model)
            elif any(keyword in model_lower for keyword in ['kling', 'veo', 'vidu', 'gen3', 'gen4']):
                video_models.append(model)
            elif any(keyword in model_lower for keyword in ['eleven', 'tts']):
                audio_models.append(model)
            else:
                chat_models.append(model)

        def chunk_list(lst, chunk_size=15):
            return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

        if chat_models:
            chat_chunks = chunk_list(chat_models)
            for i, chunk in enumerate(chat_chunks):
                field_name = "Chat Models" if i == 0 else f"Chat Models (cont. {i+1})"
                embed.add_field(name=field_name, value="\n".join(chunk), inline=True)

        if image_models:
            embed.add_field(name="Image Models", value="\n".join(image_models), inline=True)

        if video_models:
            embed.add_field(name="Video Models", value="\n".join(video_models), inline=True)

        if audio_models:
            embed.add_field(name="Audio Models", value="\n".join(audio_models), inline=True)

        embed.set_footer(text=f"Total: {len(STRAICO_MODELS)} models available")
        await ctx.send(embed=embed)

    @commands.command(name='setmodel')
    async def set_model(self, ctx, *, model_name: str = None):
        if model_name is None:
            await ctx.send("❌ Please specify a model name. Use `!models` to see available models.")
            return

        if model_name not in STRAICO_MODELS:
            similar = [m for m in STRAICO_MODELS if model_name.lower() in m.lower()]
            if similar:
                embed = discord.Embed(title="Model not found", color=0xff6b6b)
                embed.add_field(name="Did you mean one of these?", value="\n".join(similar[:10]), inline=False)
                embed.add_field(name="Usage", value=f"`!setmodel {similar[0]}`", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Model `{model_name}` not found. Use `!models` to see available models.")
            return

        self.config.user_models[ctx.author.id] = model_name
        await ctx.send(f"✅ Set your preferred model to: `{model_name}`")

    @commands.command(name='currentmodel', aliases=['current', 'mymodel'])
    async def current_model(self, ctx):
        user_model = self.config.user_models.get(ctx.author.id, self.config.default_chat_model)

        embed = discord.Embed(title="Your Current Model", color=0x00ff00)
        embed.add_field(name="Selected Model", value=f"`{user_model}`", inline=False)

        model_lower = user_model.lower()
        if any(keyword in model_lower for keyword in ['dall-e', 'flux', 'ideogram', 'imagen', 'recraft', 'bagel']):
            model_type = "🎨 Image Generation"
        elif any(keyword in model_lower for keyword in ['kling', 'veo', 'vidu', 'gen3', 'gen4']):
            model_type = "🎬 Video Generation"
        elif any(keyword in model_lower for keyword in ['eleven', 'tts']):
            model_type = "🔊 Audio Generation"
        else:
            model_type = "💬 Chat Model"

        embed.add_field(name="Type", value=model_type, inline=True)
        embed.add_field(name="Change Model", value="`!setmodel <model_name>`", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def user_info(self, ctx):
        async with ctx.typing():
            try:
                # Use persistent session and caching for user info
                user_data = await self.bot.straico_service.get_user_info()

                embed = discord.Embed(title="Straico Account Info", color=0x00ff00)

                for key, value in user_data.items():
                    if key not in ['api_key', 'token']:
                        embed.add_field(name=key.replace('_', ' ').title(), value=str(value), inline=True)

                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"Error fetching user info: {str(e)}")

    @commands.command(name='auto')
    async def toggle_auto_response(self, ctx):
        channel_id = ctx.channel.id

        if channel_id in self.config.auto_response_channels:
            self.config.auto_response_channels.remove(channel_id)
            await ctx.send("🔇 Auto-response disabled in this channel.")
        else:
            self.config.auto_response_channels.add(channel_id)
            await ctx.send("🔊 Auto-response enabled in this channel. I'll respond to all messages!")

    @commands.command(name='clear')
    async def clear_history(self, ctx):
        self.bot.conversation_history.clear_history(ctx.channel.id)
        await ctx.send("🗑️ Conversation history cleared for this channel.")

    @commands.command(name='history')
    async def show_history(self, ctx):
        history = self.bot.conversation_history.get_history(ctx.channel.id)
        if not history:
            await ctx.send("📭 No conversation history for this channel.")
            return

        history_text = f"📖 **Conversation History ({len(history)} messages):**\n"
        for i, msg in enumerate(history[-10:], 1):
            role = "🟦 User" if msg['role'] == 'user' else "🟩 Bot"
            name = f" ({msg.get('name', 'Unknown')})" if msg['role'] == 'user' else ""
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            history_text += f"\n{i}. {role}{name}: {content}"

        await ctx.send(history_text)