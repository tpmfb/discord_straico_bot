import discord
from discord.ext import commands
from typing import List
import json
from plugins.base import BasePlugin


class VideoPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "video"

    @property
    def description(self) -> str:
        return "Video generation commands"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def setup(self) -> None:
        pass

    def get_commands(self) -> List[commands.Command]:
        # Return empty list since we use decorators instead
        return []

    @commands.command(name='video')
    async def generate_video(self, ctx, *, prompt: str):
        async with ctx.typing():
            try:
                response = await self.bot.straico_service.generate_video(prompt)

                generation_id = response.get('id')
                if generation_id:
                    await ctx.send(f"🎬 Video generation started for: `{prompt}`\nGeneration ID: `{generation_id}`\nUse `!status {generation_id}` to check progress.")
                else:
                    await ctx.send(f"✅ Video generation request submitted for: `{prompt}`\nResponse: {json.dumps(response, indent=2)}")

            except Exception as e:
                await ctx.send(f"Error generating video: {str(e)}")

    @commands.command(name='status')
    async def check_status(self, ctx, generation_id: str):
        async with ctx.typing():
            try:
                status = await self.bot.straico_service.get_generation_status(generation_id)

                embed = discord.Embed(title="Generation Status", color=0xffdd59)
                embed.add_field(name="ID", value=generation_id, inline=False)

                for key, value in status.items():
                    embed.add_field(name=key.replace('_', ' ').title(), value=str(value), inline=True)

                if status.get('status') == 'completed' and 'url' in status:
                    embed.set_image(url=status['url'])

                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"Error checking status: {str(e)}")