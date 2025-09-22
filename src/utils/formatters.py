import discord
from typing import Optional, Dict, Any


def format_error_message(error: str, title: str = "Error") -> discord.Embed:
    embed = discord.Embed(title=f"❌ {title}", description=error, color=0xff0000)
    return embed


def format_success_message(message: str, title: str = "Success") -> discord.Embed:
    embed = discord.Embed(title=f"✅ {title}", description=message, color=0x00ff00)
    return embed


def format_info_message(message: str, title: str = "Information") -> discord.Embed:
    embed = discord.Embed(title=f"ℹ️ {title}", description=message, color=0x0099ff)
    return embed


def format_warning_message(message: str, title: str = "Warning") -> discord.Embed:
    embed = discord.Embed(title=f"⚠️ {title}", description=message, color=0xffaa00)
    return embed


def format_generation_status(status_data: Dict[str, Any], generation_id: str) -> discord.Embed:
    embed = discord.Embed(title="Generation Status", color=0xffdd59)
    embed.add_field(name="ID", value=generation_id, inline=False)

    for key, value in status_data.items():
        if key not in ['id', 'generation_id']:
            embed.add_field(name=key.replace('_', ' ').title(), value=str(value), inline=True)

    if status_data.get('status') == 'completed' and 'url' in status_data:
        embed.set_image(url=status_data['url'])

    return embed


def format_model_list(models: list, title: str = "Available Models", chunk_size: int = 15) -> discord.Embed:
    embed = discord.Embed(title=title, color=0x0099ff)

    def chunk_list(lst, size):
        return [lst[i:i + size] for i in range(0, len(lst), size)]

    chunks = chunk_list(models, chunk_size)

    for i, chunk in enumerate(chunks):
        field_name = "Models" if i == 0 else f"Models (cont. {i+1})"
        embed.add_field(name=field_name, value="\n".join(chunk), inline=True)

    embed.set_footer(text=f"Total: {len(models)} models available")
    return embed


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."