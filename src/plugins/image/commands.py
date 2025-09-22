import discord
from discord.ext import commands
from typing import List, Dict
import json
import re
from plugins.base import BasePlugin
from config.models import STRAICO_IMAGE_MODELS


class ImagePlugin(BasePlugin):
    def __init__(self, bot, config):
        super().__init__(bot, config)
        self.image_sessions: Dict[int, Dict] = {}

    @property
    def name(self) -> str:
        return "image"

    @property
    def description(self) -> str:
        return "Image generation commands"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def setup(self) -> None:
        pass

    def get_commands(self) -> List[commands.Command]:
        # Return empty list since we use decorators instead
        return []

    def get_listeners(self) -> List[tuple]:
        return [
            ('on_message', self.handle_image_generation_step),
        ]

    @commands.command(name='imagemodels', aliases=['imgmodels'])
    async def list_image_models(self, ctx):
        embed = discord.Embed(title="Available Image Models", color=0xff6b6b)

        model_list = []
        for i, model in enumerate(STRAICO_IMAGE_MODELS, 1):
            model_list.append(f"`{i}.` {model}")

        chunk_size = 8
        chunks = [model_list[i:i + chunk_size] for i in range(0, len(model_list), chunk_size)]

        for i, chunk in enumerate(chunks):
            field_name = "Models" if i == 0 else f"Models (cont. {i+1})"
            embed.add_field(name=field_name, value="\n".join(chunk), inline=True)

        embed.add_field(name="Usage", value="`!genimage <model_number> <prompt>`\nExample: `!genimage 7 a beautiful sunset`", inline=False)
        embed.set_footer(text=f"Total: {len(STRAICO_IMAGE_MODELS)} image models available")

        await ctx.send(embed=embed)

    @commands.command(name='genimage', aliases=['gimg'])
    async def start_image_generation(self, ctx):
        user_id = ctx.author.id

        self.image_sessions[user_id] = {
            'step': 'prompt',
            'channel_id': ctx.channel.id,
            'data': {}
        }

        embed = discord.Embed(title="🎨 Image Generation Workflow", color=0xff6b6b)
        embed.add_field(name="Step 1: Provide Your Prompt", value="Please describe what image you want to generate.\n\nExample: `a beautiful sunset over mountains`", inline=False)
        embed.add_field(name="Note", value="Just type your prompt in the next message (no command needed)", inline=False)
        await ctx.send(embed=embed)

    async def handle_image_generation_step(self, message):
        if message.author.bot:
            return

        user_id = message.author.id

        if user_id not in self.image_sessions:
            return

        if message.content.startswith(self.config.command_prefix):
            return

        session = self.image_sessions[user_id]

        if session['channel_id'] != message.channel.id:
            return

        step = session['step']

        if step == 'prompt':
            session['data']['prompt'] = message.content
            session['step'] = 'model'

            embed = discord.Embed(title="🎨 Step 2: Select Model", color=0xff6b6b)
            embed.add_field(name="Your Prompt", value=f"`{message.content}`", inline=False)

            model_list = []
            for i, model in enumerate(STRAICO_IMAGE_MODELS, 1):
                model_list.append(f"`{i}.` {model}")

            chunk_size = 5
            chunks = [model_list[i:i + chunk_size] for i in range(0, len(model_list), chunk_size)]

            for i, chunk in enumerate(chunks):
                field_name = "Available Models" if i == 0 else f"Models (cont.)"
                embed.add_field(name=field_name, value="\n".join(chunk), inline=True)

            embed.add_field(name="Next Step", value="Reply with a number (1-15) to select your model", inline=False)
            await message.channel.send(embed=embed)

        elif step == 'model':
            try:
                model_num = int(message.content.strip())
                if model_num < 1 or model_num > len(STRAICO_IMAGE_MODELS):
                    await message.channel.send(f"❌ Please choose a number between 1 and {len(STRAICO_IMAGE_MODELS)}")
                    return

                selected_model = STRAICO_IMAGE_MODELS[model_num - 1]
                session['data']['model'] = selected_model
                session['step'] = 'variations'

                embed = discord.Embed(title="🎨 Step 3: Number of Variations", color=0xff6b6b)
                embed.add_field(name="Selected Model", value=f"`{selected_model}`", inline=False)
                embed.add_field(name="Choose Variations", value="How many images would you like?\n\n`1` - Single image\n`2` - Two variations\n`3` - Three variations\n`4` - Four variations", inline=False)
                embed.add_field(name="Next Step", value="Reply with a number (1-4)", inline=False)
                await message.channel.send(embed=embed)

            except ValueError:
                await message.channel.send("❌ Please enter a valid number (1-15)")
                return

        elif step == 'variations':
            try:
                variations = int(message.content.strip())
                if variations < 1 or variations > 4:
                    await message.channel.send("❌ Please choose between 1 and 4 variations")
                    return

                session['data']['variations'] = variations
                session['step'] = 'aspect_ratio'

                embed = discord.Embed(title="🎨 Step 4: Aspect Ratio", color=0xff6b6b)
                embed.add_field(name="Variations Selected", value=f"{variations} image(s)", inline=False)
                embed.add_field(name="Choose Aspect Ratio", value="`1` - Square\n`2` - Portrait\n`3` - Landscape", inline=False)
                embed.add_field(name="Next Step", value="Reply with 1, 2, or 3", inline=False)
                await message.channel.send(embed=embed)

            except ValueError:
                await message.channel.send("❌ Please enter a valid number (1-4)")
                return

        elif step == 'aspect_ratio':
            aspect_ratios = {
                '1': ('square', 'square'),
                '2': ('portrait', 'portrait'),
                '3': ('landscape', 'landscape')
            }

            choice = message.content.strip()
            if choice not in aspect_ratios:
                await message.channel.send("❌ Please choose 1 (square), 2 (portrait), or 3 (landscape)")
                return

            aspect_name, size = aspect_ratios[choice]
            session['data']['aspect_ratio'] = aspect_name
            session['data']['size'] = size

            embed = discord.Embed(title="🎨 Generation Summary", color=0x00ff00)
            embed.add_field(name="Prompt", value=f"`{session['data']['prompt']}`", inline=False)
            embed.add_field(name="Model", value=session['data']['model'], inline=True)
            embed.add_field(name="Variations", value=str(session['data']['variations']), inline=True)
            embed.add_field(name="Aspect Ratio", value=aspect_name, inline=True)

            # Calculate estimated time based on variations
            variations = session['data']['variations']
            estimated_time = 60 + (variations * 20)  # Base 60s + 20s per variation
            embed.add_field(name="Status", value=f"🔄 Starting generation...\n⏱️ Estimated time: ~{estimated_time}s", inline=False)
            await message.channel.send(embed=embed)

            await self._generate_image_with_params(message, session['data'])

            del self.image_sessions[user_id]

    @commands.command(name='cancelimage', aliases=['cancelimg'])
    async def cancel_image_generation(self, ctx):
        user_id = ctx.author.id

        if user_id in self.image_sessions:
            del self.image_sessions[user_id]
            await ctx.send("❌ Image generation workflow cancelled.")
        else:
            await ctx.send("No active image generation workflow to cancel.")

    @commands.command(name='image')
    async def generate_image_simple(self, ctx, *, prompt: str):
        default_model = "openai/dall-e-3"

        async with ctx.typing():
            try:
                response = await self.bot.straico_service.generate_image(
                    model=default_model,
                    description=prompt,
                    size="square",
                    variations=1
                )

                images = self._extract_images(response)

                if images:
                    for image_url in images:
                        embed = discord.Embed(title="Generated Image", description=f"**Prompt:** {prompt}", color=0xff6b6b)
                        embed.add_field(name="Model", value=default_model, inline=True)
                        embed.add_field(name="Tip", value="Use `!genimage` for more options", inline=True)
                        embed.set_image(url=image_url)
                        await ctx.send(embed=embed)
                else:
                    generation_id = response.get('id') or response.get('generation_id')
                    if generation_id:
                        await ctx.send(f"🎨 Image generation started: `{prompt}`\nID: `{generation_id}`\nUse `!status {generation_id}` to check progress.")
                    else:
                        await ctx.send(f"✅ Image generation started for: `{prompt}`\nResponse: {json.dumps(response, indent=2)[:1000]}")

            except Exception as e:
                await ctx.send(f"Error generating image: {str(e)}")

    async def _generate_image_with_params(self, message, params):
        async with message.channel.typing():
            try:
                response = await self.bot.straico_service.generate_image(
                    model=params['model'],
                    description=params['prompt'],
                    size=params['size'],
                    variations=params['variations']
                )

                images = self._extract_images(response)

                if images:
                    for i, image_url in enumerate(images):
                        cleaned_url = image_url.strip()
                        if not cleaned_url.startswith(('http://', 'https://')):
                            await message.channel.send(f"❌ Invalid URL format: `{cleaned_url}`")
                            continue

                        try:
                            embed = discord.Embed(
                                title=f"✅ Generated Image {i+1}/{len(images)}" if len(images) > 1 else "✅ Generated Image",
                                description=f"**Prompt:** {params['prompt']}",
                                color=0x00ff00
                            )
                            embed.add_field(name="Model", value=params['model'], inline=True)
                            embed.add_field(name="Aspect Ratio", value=params['aspect_ratio'], inline=True)
                            embed.add_field(name="Variations", value=str(params['variations']), inline=True)
                            embed.set_image(url=cleaned_url)
                            await message.channel.send(embed=embed)
                        except discord.HTTPException as e:
                            await message.channel.send(f"✅ **Generated Image {i+1}/{len(images)}**\n**Prompt:** {params['prompt']}\n**URL:** {cleaned_url}\n*Note: Discord embed failed: {e}*")
                else:
                    generation_id = response.get('id') or response.get('generation_id')
                    if generation_id:
                        await message.channel.send(f"🎨 Image generation started!\n**ID:** `{generation_id}`\nUse `!status {generation_id}` to check progress.")
                    else:
                        await message.channel.send(f"✅ Generation submitted!\n```json\n{json.dumps(response, indent=2)[:1000]}```")

            except Exception as e:
                await message.channel.send(f"❌ Error generating image: {str(e)}")

    def _extract_images(self, response):
        images = []

        if not isinstance(response, dict):
            return images

        try:
            if 'data' in response and response['data']:
                data = response['data']
                if 'images' in data and isinstance(data['images'], list):
                    images = data['images']
                elif 'images' in data:
                    images = [data['images']]
            elif 'url' in response:
                images = [response['url']]
            elif 'image_url' in response:
                images = [response['image_url']]
            elif 'images' in response:
                if isinstance(response['images'], list):
                    images = response['images']
                else:
                    images = [response['images']]
            elif isinstance(response, dict) and 'response' in response:
                response_text = response['response']
                if 'http' in response_text:
                    url_pattern = r'https?://[^\s\'"<>]+'
                    urls = re.findall(url_pattern, response_text)
                    images = [url.rstrip('.,;!?)') for url in urls]
        except Exception:
            pass

        return images